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
        self.layer_latencies  = [1] * 314 # TODO: add to model real values
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

        ## Calculate all possible schedules
        possible_params = []
        for num_frozen in sorted(self.apps[0]["accuracies"].keys()):
            for target_fps in range(1, stream_fps + 1):
                possible_params.append((num_frozen, target_fps))

        permutations = list(itertools.product(possible_params,
                                              repeat=len(self.apps)))

        # Append app_ids to parameter permutations to make schedules
        # so that set parameters are associated explicitly with an app
        schedules = []
        app_ids = [app["app_id"] for app in self.apps]
        for perm in permutations:
            schedule = []
            for app_id, tup in zip(app_ids, perm):
                full_tup = tup + (app_id,)
                schedule.append(full_tup)
            schedules.append(schedule)

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
            metric_by_schedule[tuple(schedule)]= round(avg_metric, 4)

        ## Sort schedules by metric
        sorted_d = sorted(metric_by_schedule.items(), key=operator.itemgetter(1))
        schedules = [tup[0] for tup in sorted_d] #implicit ordering by metric
        metrics = [tup[1] for tup in sorted_d]   #implicit ordering by metric
        costs = []                               #implicit ordering by metric

        for schedule, metric in zip(schedules, metrics):
            cost = scheduler_util.get_relative_runtime(schedule,
                                                       self.layer_latencies,
                                                       self.model.final_layer)
            costs.append(cost)

        ## Optimize schedule by metric, under cost constraints

        can_degrade = True # Stopping condition when false
        can_improve = True # Stopping condition when false

        min_cost = min(costs)

        min_cost_by_metric = {}
        all_metrics = set(metrics)
        for m_val in all_metrics:
            indices = [i for i, metric in enumerate(metrics) if metric == m_val]
            min_cost_for_mval = min([costs[i] for i in indices])
            min_cost_by_metric[m_val] = min_cost_for_mval

        ## Choose best schedule
        if (min_cost > cost_threshold):
            # Get schedule that incurs the least cost to maximize chances of
            # getting the promised metric (e.g. false negative rate)

            can_degrade = False
            for schedule, metric, cost in zip(schedules, metrics, costs):
                if cost == min_cost:
                    break
        else:
            # Get schedule with minimal metric that incurs less cost than
            # cost threshold
            for schedule, metric, cost in zip(schedules, metrics, costs):
                target_cost = min_cost_by_metric[metric]
                if cost < cost_threshold and cost == target_cost:
                    if metric == min(metrics):
                        can_improve = False
                    break

        print "------------- Schedule -------------"
        pp.pprint(schedule)
        print "False neg rate:", metric, "Cost:", cost, \
              "Can degrade:", can_degrade, "Can improve:", can_improve

        ## Set parameters of schedule
        num_frozen_list = [app[0] for app in schedule]
        target_fps_list = [app[1] for app in schedule]

        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return metric, can_degrade, can_improve

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

    def get_cost_threshold(self, streamer_schedule, fpses):
        # FPSes are implicitly ordered
        # Map observed FPS to application by looking at the
        # order of task_specific apps in streamer_schedule
        fps_by_app_id = {}
        index = 0
        for nne in streamer_schedule:
            if nne["shared"]:
                continue
            app_id = nne["app_id"]
            fps_by_app_id[app_id] = fpses[index]
            index += 1
        observed_schedule = []
        for target_app in self.schedule:
            # TODO: Use getters and setters here
            num_frozen = target_app[0]
            target_fps = target_app[1]
            app_id = target_app[2]
            observed_fps = fps_by_app_id[app_id]
            observed_app = (num_frozen, observed_fps)
            observed_schedule.append(observed_app)
            print "Target FPS: ", target_fps, "Observed FPS: ", observed_fps
        target_cost = scheduler_util.get_relative_runtime(self.schedule,
                                                          self.layer_latencies,
                                                          self.model.final_layer)
        observed_cost = scheduler_util.get_relative_runtime(observed_schedule,
                                                          self.layer_latencies,
                                                          self.model.final_layer)
        print "Target cost: ", target_cost, " Observed cost: ", observed_cost
        if abs(target_cost - observed_cost) / target_cost < 0.2:
            return -1
        return observed_cost

    def run(self, cost_threshold):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        can_degrade = True
        can_improve = True

        while cost_threshold > 0 and can_degrade and can_improve:
            # Get parameters
            metric, can_degrade, can_improve = self.optimize_parameters(cost_threshold)

            # Get streamer schedule
            sched = self.make_streamer_schedule()

            # Deploy schedule
            fpses = []

            socket.send_json(sched)
            fps_message = socket.recv()
            fpses = fps_message.split(",")
            fpses = [float(fps) for fps in fpses]

            cost_threshold = self.get_cost_threshold(sched, fpses)

        rel_accs = self.get_relative_accuracies()

        return metric, np.average(rel_accs), self.num_frozen_list, self.target_fps_list
