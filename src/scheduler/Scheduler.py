import sys
sys.path.append('src/scheduler')
import scheduler_util
import Schedule
import numpy as np
import operator
import zmq


class Scheduler:
    ### Object that performs optimization of parameters
    ### and feedback with Streamer

    def __init__(self, apps, video_desc, model_desc):
        self.apps = apps
        self.video_desc = video_desc
        self.model = Schedule.Model(model_desc)
        self.num_frozen_list = []
        self.target_fps_list = []

    def get_relative_accuracies(self):
        rel_accs = []
        for app, num_frozen in zip(self.apps, self.num_frozen_list):
            max_acc = max(app["accuracies"].values())
            cur_acc = app["accuracies"][num_frozen]
            rel_acc = (max_acc - cur_acc) / max_acc
            rel_accs.append(rel_acc)
        return rel_accs

    def optimize_parameters(self):

        stream_fps = self.video_desc["stream_fps"]
        metric_by_params = {}
        for target_fps in range(1, stream_fps + 1):
            for app in self.apps:
                num_frozens = sorted(app["accuracies"].keys())
                for num_frozen in num_frozens:
                    accuracy = app["accuracies"][num_frozen]
                    false_neg_rate = scheduler_util.get_false_neg_rate(
                                                      accuracy,
                                                      app["event_length_ms"],
                                                      stream_fps,
                                                      target_fps)
                    params = (target_fps, num_frozen)
                    metric_by_params[params] = round(false_neg_rate, 4)

        sorted_d = sorted(metric_by_params.items(), key=operator.itemgetter(1))
        params = [tup[0] for tup in sorted_d]

        num_frozen_list = [87, 87, 87]
        target_fps_list = [2, 4, 4]

        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return

    def make_streamer_schedule_no_sharing(self):

        s = Schedule.Schedule()

        for app in self.apps:
            net = Schedule.NeuralNet(s.get_id(),
                                     self.model,
                                     -1,
                                     1,
                                     self.model.final_layer,
                                     False,
                                     self.video_desc["stream_fps"],
                                     app["model_path"])
            s.add_neural_net(net)
        return s.schedule

    def make_streamer_schedule(self):

        for app, num_frozen, target_fps \
                in zip(self.apps, self.num_frozen_list, self.target_fps_list):
            app["num_frozen"] = num_frozen
            app["target_fps"] = target_fps

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
            if len(future_apps) > 0 or len(self.apps) == 1:

                # Set target_fps depending on children target_fps
                if len(future_apps) > 0:
                    parent_target_fps = max([app["target_fps"]
                                                for app in future_apps])
                else:
                    parent_target_fps = self.video_desc["stream_fps"],

                net = Schedule.NeuralNet(s.get_id(),
                                         self.model,
                                         parent_net.net_id,
                                         last_shared_layer,
                                         min_frozen,
                                         True,
                                         parent_target_fps,
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
                                         app["target_fps"],
                                         app["model_path"])
                s.add_neural_net(net)
                num_apps_done += 1

            last_shared_layer = parent_net.end

        return s.schedule

    def run(self):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # Get parameters
        self.optimize_parameters()

        # Get streamer schedule
        sched = self.make_streamer_schedule_no_sharing()

        # Deploy schedule
        fpses = []

        socket.send_json(sched)
        fps_message = socket.recv()
        fpses = fps_message.split(",")

        rel_accs = self.get_relative_accuracies()

        return np.average(rel_accs), self.num_frozen_list
