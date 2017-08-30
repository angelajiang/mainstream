import sys
sys.path.append('src/scheduler')
import Schedule
import numpy as np
import zmq

# Create schedule = Scheduler(apps, video_desc, model_desc)
# schedule.run()

class Scheduler:
    ### Object that performs optimization of parameters
    ### and feedback with Streamer
    def __init__(self, apps, video_desc, model_desc):
        self.apps = apps
        self.video_desc = video_desc
        self.model = Schedule.Model(model_desc)
        self.num_frozen_list = []
        self.target_fps_list = []

    def optimize_parameters(self):
        ## Optimizes for minimizing false negative rate
        ## Calculates 1) num_frozen 2) stride for each application
        ## Returns num_frozen_list and stride_list
        return [], []

    def make_streamer_schedule_no_sharing(self):

        s = Schedule.Schedule()

        for app in self.apps:
            net = Schedule.NeuralNet(s.get_id(),
                                     self.model,
                                     -1,
                                     1,
                                     self.model.final_layer,
                                     False,
                                     app["model_path"])
            s.add_neural_net(net)
        return s.schedule

    def make_streamer_schedule(self):

        for app, num_frozen in zip(self.apps, self.num_frozen_list):
            app["num_frozen"] = num_frozen

        s = Schedule.Schedule()

        num_apps_done = 0
        last_shared_layer = 1

        parent_net = Schedule.NeuralNet(-1, self.model, end=1)

        while (num_apps_done < len(self.apps)):
            min_frozen = min([app["num_frozen"] \
                for app in self.apps if app["num_frozen"] > last_shared_layer])
            min_apps    = [app for app in self.apps \
                            if app["num_frozen"] == min_frozen]
            future_apps = [app for app in self.apps \
                            if app["num_frozen"] > min_frozen]

            # Check if we need to share part of the NN, and make a base NN
            # If so, we make it and set it as the parent
            if len(future_apps) > 0 or len(min_apps) == len(self.apps):
                net = Schedule.NeuralNet(s.get_id(),
                                         self.model,
                                         parent_net.net_id,
                                         last_shared_layer,
                                         min_frozen,
                                         True,
                                         min_apps[0]["model_path"])
                s.add_neural_net(net)
                parent_net = net

            # Make app-specific NN that is branched off the parent
            # Parent is either nothing or the last shared branch
            for app in min_apps:
                net = Schedule.NeuralNet(s.get_id(),
                                         self.model,
                                         parent_net.net_id,
                                         parent_net.end,
                                         self.model.final_layer,
                                         False,
                                         app["model_path"])
                s.add_neural_net(net)
                num_apps_done += 1

            last_shared_layer = parent_net.end

        return s.schedule

    def run(self):
        ### Run function invokes scheduler and streamer feedback cycle

        num_trials = 1
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # Get parameters

        # Get streamer schedule
        sched = scheduler.make_streamer_schedule_no_sharing(self.apps,
                                                            self.model_desc)

        # Deploy schedule
        fpses = []
        for i in range(num_trials):
            socket.send_json(sched)
            fps_message = socket.recv()
            fpses.append(float(fps_message))
        avg_fps = np.average(fpses)
        stdev = np.std(fpses)

        #rel_accs = [get_relative_accuracy(app, num_frozen) \
        #                for app, num_frozen in zip(self.apps, num_frozen_list)]
        rel_accs = [1 for app in self.apps]

        return np.average(rel_accs), self.num_frozen_list
