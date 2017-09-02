import sys
sys.path.append('src/scheduler')
import scheduler_util
import Schedule
import itertools
import numpy as np
import operator
import pprint as pp
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

    def optimize_parameters(self, cost_threshold):

        stream_fps = self.video_desc["stream_fps"]
        layer_latencies = [1] * 314

        ## Calculate all possible schedules
        possible_params = []
        for num_frozen in sorted(self.apps[0]["accuracies"].keys()):
            for target_fps in range(1, stream_fps + 1):
                possible_params.append((num_frozen, target_fps))

        schedules = list(itertools.product(possible_params,
                                           repeat=len(self.apps)))

        ## Calculate the metric you're optimizing for for each schedule
        metric_by_schedule = {}
        for schedule in schedules:
            total_metric = 0.0
            for i, params in enumerate(schedule):
                app = self.apps[i]

                num_frozen = params[0]
                target_fps = params[1]

                accuracy = app["accuracies"][num_frozen]
                false_neg_rate = scheduler_util.get_false_neg_rate(
                                                  accuracy,
                                                  app["event_length_ms"],
                                                  stream_fps,
                                                  target_fps)
                total_metric += false_neg_rate

            avg_metric = total_metric / len(self.apps)
            metric_by_schedule[schedule]= round(avg_metric, 4)

        ## Sort schedules by metric
        sorted_d = sorted(metric_by_schedule.items(), key=operator.itemgetter(1))
        schedules = [tup[0] for tup in sorted_d] #implicit ordering
        metrics = [tup[1] for tup in sorted_d]   #implicit ordering
        costs = []                               #implicit ordering

        for schedule in schedules:
            cost = scheduler_util.get_relative_runtime(schedule,
                                                     layer_latencies,
                                                     self.model.final_layer)
            costs.append(cost)

        ## Optimize schedule by metric, under cost constraints

        can_degrade = True # Return value which tells us if there is any point in rescheduling

        min_cost = min(costs)
        print "------ Schedule --------"
        if (min_cost > cost_threshold):
            # Get schedule that incurs the least cost to maximize chances of
            # getting the promised metric (e.g. false negative rate)

            print "[WARNING] No schedule has cost under", cost_threshold
            can_degrade = False

            for schedule, metric, cost in zip(schedules, metrics, costs):
                if cost == min_cost:
                    pp.pprint(schedule)
                    print "False neg rate:", metric, "Cost:", cost, "Can degrade:", can_degrade
                    break
        else:
            # Get schedule with minimal metric that incurs less cost than
            # cost threshold
            for schedule, metric, cost in zip(schedules, metrics, costs):
                if cost < cost_threshold:
                    pp.pprint(schedule)
                    print "False neg rate:", metric, "Cost:", cost, "Can degrade:", can_degrade
                    break


        # Set parameters of schedule

        num_frozen_list = [app[0] for app in schedule]
        target_fps_list = [app[1] for app in schedule]

        num_frozen_list = [249, 249]
        target_fps_list = [1, 10]

        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return can_degrade

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

        apps = []
        for app, num_frozen, target_fps \
                in zip(self.apps, self.num_frozen_list, self.target_fps_list):
            a = app.copy()
            a["num_frozen"] = num_frozen
            a["target_fps"] = target_fps
            apps.append(a)

        s = Schedule.Schedule()

        num_apps_done = 0
        last_shared_layer = 1
        parent_net = Schedule.NeuralNet(-1, -1, self.model, end=1)

        while (num_apps_done < len(apps)):
            min_frozen = min([app["num_frozen"] \
                for app in apps if app["num_frozen"] > last_shared_layer])
            min_apps    = [app for app in apps \
                            if app["num_frozen"] == min_frozen]
            future_apps = [app for app in apps \
                            if app["num_frozen"] > min_frozen]

            # Check if we need to share part of the NN, and make a base NN
            # If so, we make it and set it as the parent
            if len(future_apps) > 0 or len(apps) == len(min_apps):

                # Set target_fps depending on children target_fps
                if len(future_apps) > 0:
                    parent_target_fps = max([app["target_fps"]
                                                for app in future_apps])
                else:
                    parent_target_fps = max([app["target_fps"]
                                                for app in min_apps])

                net = Schedule.NeuralNet(s.get_id(),
                                         -1,
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
                                         app["app_id"],
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

    def get_cost_threshold(self, schedule, fpses):
        target_fpses = []
        for nne in schedule:
            if not nne["shared"]:
                target_fps = nne["target_fps"]
                target_fpses.append(target_fps)
        for target, observed in zip(target_fpses, fpses):
            print target, observed

    def run(self, cost_threshold):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # Get parameters
        self.optimize_parameters(cost_threshold)

        # Get streamer schedule
        sched = self.make_streamer_schedule()
        pp.pprint(sched)

        # Deploy schedule
        fpses = []

        socket.send_json(sched)
        fps_message = socket.recv()
        fpses = fps_message.split(",")

        self.get_cost_threshold(sched, fpses)

        rel_accs = self.get_relative_accuracies()

        return np.average(rel_accs), self.num_frozen_list
