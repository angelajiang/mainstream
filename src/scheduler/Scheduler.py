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

    def __init__(self, apps, video_desc, model_desc, sigma):
        self.apps = apps
        self.video_desc = video_desc
        self.model = Schedule.Model(model_desc)
        self.num_frozen_list = []
        self.target_fps_list = []
        self.sigma = sigma

        # Only calculate distribution around each accuracy once
        # to minimize randomness. Used to calculate false negative rate.
        acc_dists = {}
        for app in apps:
            accs = app["accuracies"].values()
            for acc in accs:
                if acc not in acc_dists.keys():
                    acc_dist = scheduler_util.get_acc_dist(acc, self.sigma)
                    acc_dists[acc] = acc_dist
        self.acc_dists = acc_dists

    def get_relative_accuracies(self):
        rel_accs = []
        for unit in self.schedule:
            max_acc = max(unit.app["accuracies"].values())
            cur_acc = unit.app["accuracies"][unit.num_frozen]
            rel_acc = (max_acc - cur_acc) / max_acc
            rel_accs.append(rel_acc)
        return rel_accs

    def get_parameter_options(self):

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
                for a in self.apps:
                    if a["app_id"] == app_id:
                        app = a
                unit = Schedule.ScheduleUnit(app, tup[1], tup[0])
                schedule.append(unit)
            schedules.append(schedule)

        ## Calculate the metric you're optimizing for for each schedule
        metric_by_schedule = {}
        for schedule in schedules:
            total_metric = 0.0
            for unit in schedule:
                app = unit.app
                num_frozen = unit.num_frozen
                target_fps = unit.target_fps

                accuracy = app["accuracies"][num_frozen]
                false_neg_rate = scheduler_util.get_false_neg_rate(
                                                  self.acc_dists[accuracy],
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
            cost = scheduler_util.get_cost_schedule(schedule,
                                                    self.model.layer_latencies,
                                                    self.model.final_layer)
            costs.append(cost)
        return schedules, metrics, costs

    def optimize_parameters(self, cost_threshold):

        stream_fps = self.video_desc["stream_fps"]

        ## Calculate all possible schedules
        possible_params = []
        for num_frozen in sorted(self.apps[0]["accuracies"].keys()):
            for target_fps in range(1, stream_fps + 1):
                possible_params.append((num_frozen, target_fps))

        cost_benefits = {}

        target_fps_options = range(1, stream_fps + 1)

        current_schedule = []

        for app in self.apps:
            app_id = app["app_id"]
            cost_benefits[app_id] = {}
            num_frozen_options = app["accuracies"].keys()
            for num_frozen in sorted(num_frozen_options):
                if num_frozen not in cost_benefits[app_id].keys():
                    cost_benefits[app_id][num_frozen] = {}
                for target_fps in target_fps_options:
                    accuracy = app["accuracies"][num_frozen]
                    benefit = scheduler_util.get_false_neg_rate(
                                                      self.acc_dists[accuracy],
                                                      app["event_length_ms"],
                                                      stream_fps,
                                                      target_fps)
                    cost = scheduler_util.get_cost(num_frozen,
                                                   target_fps,
                                                   self.model.layer_latencies)
                    cost_benefits[app_id][num_frozen][target_fps] = (cost, benefit)
            best_target_fps = max(target_fps_options)
            best_num_frozen = min(num_frozen_options)
            current_schedule.append(Schedule.ScheduleUnit(app, best_target_fps, best_num_frozen))

        current_cost = scheduler_util.get_cost_schedule(current_schedule,
                                                        self.model.layer_latencies,
                                                        self.model.final_layer)

        updated = False # Stopping condition when there is no way to reach cost_threshold
        while (current_cost > cost_threshold):
            # Get next best change to schedule
            # Upgrade is (target_fps, #frozen) with better than
            # cost and smallest cost/benefit across all apps
            min_cost_benefit = 10000000
            best_new_unit = -1
            best_new_schedule = current_schedule
            for unit in current_schedule:
                cur_target_fps = unit.target_fps
                cur_num_frozen = unit.num_frozen
                app_id = unit.app_id
                app = unit.app
                cur_accuracy = app["accuracies"][cur_num_frozen]
                cur_metric = scheduler_util.get_false_neg_rate(
                                                  self.acc_dists[cur_accuracy],
                                                  app["event_length_ms"],
                                                  stream_fps,
                                                  cur_target_fps)

                for potential_target_fps in target_fps_options:
                    for potential_num_frozen in sorted(num_frozen_options):
                        # Skip if it is not a change
                        for u in current_schedule:
                            if u.app_id == app_id:
                                if (u.num_frozen == potential_num_frozen) and \
                                        (u.target_fps == potential_target_fps):
                                            continue
                        cost_benefit_tup = \
                            cost_benefits[app_id][potential_num_frozen][potential_target_fps]
                        cost_benefit = cost_benefit_tup[1] / float(cost_benefit_tup[0])
                        if cost_benefit < min_cost_benefit:

                            # Is a candidate move. Check that it lowers cost

                            potential_unit = Schedule.ScheduleUnit(app,
                                                      potential_target_fps,
                                                      potential_num_frozen)
                            potential_schedule = []
                            for c_unit in current_schedule:
                                if c_unit.app_id == potential_unit.app_id:
                                    potential_schedule.append(potential_unit)
                                else:
                                    potential_schedule.append(c_unit)
                            current_app_cost = scheduler_util.get_cost(cur_num_frozen,
                                                                         cur_target_fps,
                                                                        self.model.layer_latencies)
                            potential_app_cost = scheduler_util.get_cost(potential_num_frozen,
                                                                         potential_target_fps,
                                                                        self.model.layer_latencies)

                            if potential_app_cost < current_app_cost:
                                min_cost_benefit = cost_benefit
                                best_new_unit = potential_unit
                                best_new_schedule = potential_schedule
                                updated = True

            new_cost = scheduler_util.get_cost_schedule(best_new_schedule,
                                                        self.model.layer_latencies,
                                                        self.model.final_layer)
            if not updated:
                break
            else:
                current_cost = new_cost
                current_schedule = best_new_schedule
                updated = False

        # Get average metric over final schedule
        total_metric = 0
        for unit in current_schedule:
            target_fps = unit.target_fps
            num_frozen = unit.num_frozen
            app_id = unit.app_id
            app = unit.app
            accuracy = app["accuracies"][num_frozen]
            metric = scheduler_util.get_false_neg_rate(
                                          self.acc_dists[accuracy],
                                          app["event_length_ms"],
                                          stream_fps,
                                          target_fps)
            total_metric += metric
        average_metric = round(total_metric / float(len(self.apps)), 4)

        print "------------- Schedule -------------"
        for unit in current_schedule:
            print "App:", unit.app_id, "- num_frozen:", unit.num_frozen, ", target_fps:", unit.target_fps
        print "False neg rate:", average_metric, "Cost:", current_cost

        ## Set parameters of schedule
        num_frozen_list = [unit.num_frozen for unit in current_schedule]
        target_fps_list = [unit.target_fps for unit in current_schedule]

        self.schedule = current_schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return average_metric

    def optimize_parameters_old(self, cost_threshold):

        schedules, metrics, costs = self.get_parameter_options()

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
                if cost <= cost_threshold and cost == target_cost:
                    if metric == min(metrics):
                        can_improve = False
                    break

        ## Set parameters of schedule
        num_frozen_list = [app[0] for app in schedule]
        target_fps_list = [app[1] for app in schedule]

        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return metric, can_degrade, can_improve

    def make_streamer_schedule_no_sharing(self):

        s = Schedule.StreamerSchedule()

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

        s = Schedule.StreamerSchedule()

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
        print "[get_cost_threshold] Recalculating..."
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
        for unit in self.schedule:
            # TODO: Use getters and setters here
            target_fps = unit.target_fps
            observed_fps = fps_by_app_id[unit.app_id]
            observed_unit = Schedule.ScheduleUnit(unit.app,
                                                  observed_fps,
                                                  unit.num_frozen)
            observed_schedule.append(observed_unit)
            print "[get_cost_threshold] Target FPS: ", target_fps, "Observed FPS: ", observed_fps
        target_cost = scheduler_util.get_cost_schedule(self.schedule,
                                                       self.model.layer_latencies,
                                                       self.model.final_layer)
        observed_cost = scheduler_util.get_cost_schedule(observed_schedule,
                                                         self.model.layer_latencies,
                                                         self.model.final_layer)
        print "[get_cost_threshold] Target cost: ", target_cost, " Observed cost: ", observed_cost
        if abs(target_cost - observed_cost) / target_cost < 0.1:
            return -1
        return observed_cost

    def run(self, cost_threshold):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        num_trials = 3
        can_improve = True
        last_metric = -1

        while cost_threshold > 0 and can_improve:
            # Get parameters
            metric = self.optimize_parameters(cost_threshold)
            if metric == last_metric:
                can_improve = False

            last_metric = metric

            # Get streamer schedule
            sched = self.make_streamer_schedule()

            # Deploy schedule
            thresholds = []
            for i in range(num_trials):
                socket.send_json(sched)
                fps_message = socket.recv()
                fpses = fps_message.split(",")
                fpses = [float(fps) for fps in fpses]
                threshold = self.get_cost_threshold(sched, fpses)
                thresholds.append(threshold)
            cost_threshold = np.average(thresholds)

        rel_accs = self.get_relative_accuracies()

        return metric, np.average(rel_accs), self.num_frozen_list, self.target_fps_list
