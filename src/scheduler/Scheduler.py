import sys
sys.path.append('src/scheduler')
import scheduler_util
import Schedule
import itertools
import operator
import pprint as pp
import zmq


class Scheduler:
    ### Object that performs optimization of parameters
    ### and feedback with Streamer

    def __init__(self, metric, apps, video_desc, model_desc, sigma):
        assert metric == "f1" or metric == "fnr" or metric == "fpr" or metric == "f1-x"

        self.apps = apps
        self.video_desc = video_desc
        self.metric = metric
        self.model = Schedule.Model(model_desc)
        self.num_frozen_list = []
        self.target_fps_list = []
        self.sigma = sigma
        self.stream_fps = self.video_desc["stream_fps"]

    def get_relative_accuracies(self):
        rel_accs = []
        for unit in self.schedule:
            max_acc = max(unit.app["accuracies"].values())
            cur_acc = unit.app["accuracies"][unit.num_frozen]
            rel_acc = (max_acc - cur_acc) / max_acc
            rel_accs.append(rel_acc)
        return rel_accs

    def get_parameter_options(self):

        ## Calculate all possible schedules
        possible_params = []
        for num_frozen in sorted(self.apps[0]["accuracies"].keys()):
            for target_fps in range(1, self.stream_fps + 1):
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

        ## Calculate the metric you're minimizing for, for each schedule
        metric_by_schedule = {}
        for schedule in schedules:
            total_metric = 0.0
            for unit in schedule:
                app = unit.app
                num_frozen = unit.num_frozen
                target_fps = unit.target_fps

                metric = self.get_metric(app,
                                         num_frozen,
                                         target_fps)

                total_metric += metric

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

    def set_schedule_values(self, schedule):
        # Get average metric over final schedule
        # Sets self.schedule, self.num_frozen_list, self.target_fps_list

        metrics = []
        target_fps_list = []
        num_frozen_list = []
        for unit in schedule:
            target_fps = unit.target_fps
            num_frozen = unit.num_frozen
            app_id = unit.app_id
            app = unit.app
            metric = self.get_metric(app,
                                     num_frozen,
                                     target_fps)

            target_fps_list.append(target_fps)
            num_frozen_list.append(num_frozen)
            metrics.append(metric)

        average_metric = sum(metrics) / float(len(metrics))

        ## Print schedule
        print "------------- Schedule -------------"
        for unit in schedule:
            print "App:", unit.app_id, "- num_frozen:", unit.num_frozen, ", target_fps:", unit.target_fps
        print "Avg F1-score:", 1 - average_metric

        ## Set parameters of schedule
        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return average_metric

    def set_schedule_values_metric(self, schedule):
        # Same as set_schedule_values except returns list of metric values
        metrics = []
        target_fps_list = []
        num_frozen_list = []
        for unit in schedule:
            target_fps = unit.target_fps
            num_frozen = unit.num_frozen
            app_id = unit.app_id
            app = unit.app
            metric = self.get_metric(app,
                                     num_frozen,
                                     target_fps)

            target_fps_list.append(target_fps)
            num_frozen_list.append(num_frozen)
            metrics.append(metric)
        print "------------- Schedule -------------"
        for unit in schedule:
            print "App:", unit.app_id, "- num_frozen:", unit.num_frozen, ", target_fps:", unit.target_fps

        ## Set parameters of schedule
        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return metrics

    def set_max_parameters(self):
        # Makes schedule which uses max sharing and max target_fps
        # Sets self.schedule, self.num_frozen_list, self.target_fps_list

        schedule = []
        num_frozen_list = []
        target_fps_list = []
        for app in self.apps:
            app_id = app["app_id"]
            num_frozen = max(app["accuracies"].keys())
            target_fps = self.stream_fps
            unit = Schedule.ScheduleUnit(app,
                                         target_fps,
                                         num_frozen)
            num_frozen_list.append(num_frozen)
            target_fps_list.append(target_fps)
            schedule.append(unit)
        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        cost = scheduler_util.get_cost_schedule(schedule,
                                                self.model.layer_latencies,
                                                self.model.final_layer)

        average_metric = self.set_schedule_values(schedule)

        return average_metric


    def get_metric(self, app, num_frozen, target_fps):
        # "self.metric" is metric to minimize. In set {"f1", "fnr", "fpr"}
        accuracy = app["accuracies"][num_frozen]
        if self.metric == "f1":
            prob_tnr = app["prob_tnrs"][num_frozen]
            f1 = scheduler_util.get_f1_score(accuracy,
                                             prob_tnr,
                                             app["event_length_ms"],
                                             app["event_frequency"],
                                             app["correlation"],
                                             self.stream_fps,
                                             target_fps)
            metric = 1 - f1
        elif self.metric == "f1-x":
            prob_tnr = app["prob_tnrs"][num_frozen]
            x_vote = app["x_vote"]
            f1 = scheduler_util.get_f1_score(accuracy,
                                             prob_tnr,
                                             app["event_length_ms"],
                                             app["event_frequency"],
                                             app["correlation"],
                                             self.stream_fps,
                                             target_fps,
                                             x_vote = x_vote)
            metric = 1 - f1
        elif self.metric == "fnr":
            metric = scheduler_util.get_false_neg_rate(accuracy,
                                                       app["event_length_ms"],
                                                       app["correlation"],
                                                       self.stream_fps,
                                                       target_fps)
        elif self.metric == "fpr":
            prob_tnr = app["prob_tnrs"][num_frozen]
            metric = scheduler_util.get_false_pos_rate(
                                              accuracy,
                                              prob_tnr,
                                              app["event_length_ms"],
                                              app["event_frequency"],
                                              app["correlation"],
                                              self.stream_fps,
                                              target_fps)
        else:
            print "Didn't recognize metric %s. Exiting." % (self.metric)
            sys.exit()
        return metric

    def optimize_parameters(self, cost_threshold):
        # Makes schedule with optimal choices for num_frozen and target_fps
        # Sets self.schedule, self.num_frozen_list, self.target_fps_list

        ## Calculate all possible schedules
        possible_params = []
        target_fps_options = range(1, self.stream_fps + 1)
        for num_frozen in sorted(self.apps[0]["accuracies"].keys()):
            for target_fps in target_fps_options:
                possible_params.append((num_frozen, target_fps))

        cost_benefits = {}

        current_schedule = []

        for app in self.apps:
            app_id = app["app_id"]
            cost_benefits[app_id] = {}
            num_frozen_options = app["accuracies"].keys()
            for num_frozen in reversed(sorted(num_frozen_options)):
                if num_frozen not in cost_benefits[app_id].keys():
                    cost_benefits[app_id][num_frozen] = {}
                for target_fps in target_fps_options:
                    benefit = self.get_metric(app,
                                              num_frozen,
                                              target_fps)
                    cost = scheduler_util.get_cost(num_frozen,
                                                   target_fps,
                                                   self.model.layer_latencies)
                    cost_benefits[app_id][num_frozen][target_fps] = (cost,
                                                                     benefit)
            cheapest_target_fps = min(target_fps_options)
            cheapest_num_frozen = max(num_frozen_options)
            current_schedule.append(Schedule.ScheduleUnit(app,
                                                          cheapest_target_fps,
                                                          cheapest_num_frozen))

        ## Make moves in order of maximal cost/benefit
        ## which decrease the metric and fit the budget
        updated = True # Stopping condition
        while (updated):
            updated = False
            # Get next best change to schedule
            # Upgrade is (target_fps, #frozen) with larger
            # cost and largest cost/benefit across all apps
            max_cost_benefit = 0
            best_new_unit = -1
            for unit in current_schedule:
                cur_target_fps = unit.target_fps
                cur_num_frozen = unit.num_frozen
                app_id = unit.app_id
                app = unit.app
                cur_metric = self.get_metric(app,
                                             cur_num_frozen,
                                             cur_target_fps)

                for potential_target_fps in target_fps_options:
                    for potential_num_frozen in sorted(num_frozen_options):
                        # Skip if it is not a change
                        u_apps = [u for u in current_schedule if u.app_id == app_id]
                        if (u_apps[0].num_frozen == potential_num_frozen and
                            u_apps[0].target_fps == potential_target_fps):
                            continue

                        cost_benefit_tup = \
                            cost_benefits[app_id][potential_num_frozen][potential_target_fps]
                        cost_benefit = cost_benefit_tup[1] / float(cost_benefit_tup[0])
                        potential_metric = self.get_metric(app,
                                                           potential_num_frozen,
                                                           potential_target_fps)
                        if potential_metric < cur_metric and cost_benefit > max_cost_benefit:

                                # Check that move its within budget
                                potential_unit = Schedule.ScheduleUnit(app,
                                                          potential_target_fps,
                                                          potential_num_frozen)
                                potential_schedule = []
                                for c_unit in current_schedule:
                                    if c_unit.app_id == potential_unit.app_id:
                                        potential_schedule.append(potential_unit)
                                    else:
                                        copy_unit = Schedule.ScheduleUnit(c_unit.app,
                                                                  c_unit.target_fps,
                                                                  c_unit.num_frozen)
                                        potential_schedule.append(copy_unit)
                                potential_sched_cost = scheduler_util.get_cost_schedule(potential_schedule,
                                                                                    self.model.layer_latencies,
                                                                                    self.model.final_layer)

                                if potential_sched_cost <= cost_threshold:
                                    cost = potential_sched_cost
                                    max_cost_benefit = cost_benefit
                                    best_new_unit = potential_unit
                                    best_new_schedule = potential_schedule
                                    updated = True

            if updated:
                current_schedule = best_new_schedule

        average_metric = self.set_schedule_values(current_schedule)

        return average_metric

    def optimize_per_app(self, cost_threshold):
        # Optimizes by giving equal cost to each app
        costs = scheduler_util.get_alloc_cost_per_app(self.apps, cost_threshold)
        #print "Cost allocated: ", costs
        current_schedule = []
        target_fps_options = range(1, self.stream_fps + 1)

        cost_benefits = {}

        for app in self.apps:
            app_id = app["app_id"]
            cost_benefits[app_id] = {}
            num_frozen_options = sorted(app["accuracies"].keys())
            for num_frozen in reversed(num_frozen_options):
                if num_frozen not in cost_benefits[app_id].keys():
                    cost_benefits[app_id][num_frozen] = {}
                for target_fps in target_fps_options:
                    benefit = self.get_metric(app,
                                              num_frozen,
                                              target_fps)
                    cost = scheduler_util.get_cost(num_frozen,
                                                   target_fps,
                                                   self.model.layer_latencies)
                    cost_benefits[app_id][num_frozen][target_fps] = (cost, benefit)
            cheapest_target_fps = min(target_fps_options)
            cheapest_num_frozen = max(num_frozen_options)
            current_schedule.append(Schedule.ScheduleUnit(app,
                                                          cheapest_target_fps,
                                                          cheapest_num_frozen))

        ## In order of app id, chooses the model with minimum metric
        ## and fit the budget

        updated = True
        while (updated):
            updated = False
            max_benefit = 0
            best_new_unit = -1
            for unit in current_schedule:
                cur_target_fps = unit.target_fps
                cur_num_frozen = unit.num_frozen
                app_id = unit.app_id
                app = unit.app
                cur_metric = self.get_metric(app,
                                             cur_num_frozen,
                                             cur_target_fps)
                current_sched_cost = scheduler_util.get_cost_schedule(current_schedule,
                                                    self.model.layer_latencies,
                                                    self.model.final_layer)

                for potential_target_fps in target_fps_options:
                    for potential_num_frozen in num_frozen_options:
                        potential_metric = self.get_metric(app,
                                                           potential_num_frozen,
                                                           potential_target_fps)
                        cost_benefit_tup = cost_benefits[app_id][potential_num_frozen][potential_target_fps]
                        benefit = cost_benefit_tup[0]
                        if potential_metric < cur_metric and benefit > max_benefit:
                            potential_unit = Schedule.ScheduleUnit(app,
                                                      potential_target_fps,
                                                      potential_num_frozen)
                            potential_schedule = []
                            for c_unit in current_schedule:
                                if c_unit.app_id == potential_unit.app_id:
                                    potential_schedule.append(potential_unit)
                                else:
                                    copy_unit = Schedule.ScheduleUnit(c_unit.app,
                                                         c_unit.target_fps,
                                                         c_unit.num_frozen)
                                    potential_schedule.append(copy_unit)
                            potential_sched_cost = scheduler_util.get_cost_schedule(potential_schedule,
                                                                  self.model.layer_latencies,
                                                                  self.model.final_layer)

                            scheduled_cost_app = scheduler_util.get_cost_per_app(self.apps,
                                                                        potential_schedule,
                                                                        self.model.layer_latencies,
                                                                        self.model.final_layer)

                            if potential_sched_cost <= cost_threshold and scheduled_cost_app[app_id] <= costs[app_id]:
                                max_benefit = benefit
                                best_new_unit = potential_unit
                                best_new_schedule = potential_schedule
                                updated = True

                if updated:
                    current_schedule = best_new_schedule

            final_cost_app = scheduler_util.get_cost_per_app(self.apps,
                                                        current_schedule,
                                                        self.model.layer_latencies,
                                                        self.model.final_layer)
            #print "Final Costs: ", final_cost_app
            metrics = self.set_schedule_values_metric(current_schedule)
            return metrics

        def make_streamer_schedule_no_sharing(self):

            s = Schedule.StreamerSchedule()

            for app in self.apps:
                num_frozen = min(app["accuracies"].keys())
                net = Schedule.NeuralNet(s.get_id(),
                                         app["app_id"],
                                         self.model,
                                     -1,
                                     1,
                                     self.model.final_layer,
                                     False,
                                     self.video_desc["stream_fps"],
                                     app["model_path"][num_frozen])
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
                                         min_apps[0]["model_path"][min_frozen])
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
                                         app["model_path"][min_frozen])
                s.add_neural_net(net)
                num_apps_done += 1

            last_shared_layer = parent_net.end

        return s.schedule

    def get_fps_by_app_id(self, streamer_schedule, fpses):
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
        return fps_by_app_id

    def get_observed_performance(self, streamer_schedule, fpses):
        fps_by_app_id = self.get_fps_by_app_id(streamer_schedule, fpses)
        fnrs = []
        fprs = []
        observed_schedule = []
        for app, num_frozen in zip(self.apps, self.num_frozen_list):

            observed_fps = fps_by_app_id[app["app_id"]]

            accuracy = app["accuracies"][num_frozen]
            prob_tnr = app["prob_tnrs"][num_frozen]
            false_neg_rate = scheduler_util.get_false_neg_rate(
                                              accuracy,
                                              app["event_length_ms"],
                                              app["correlation"],
                                              self.stream_fps,
                                              observed_fps)
            false_pos_rate = scheduler_util.get_false_pos_rate(
                                              accuracy,
                                              prob_tnr,
                                              app["event_length_ms"],
                                              app["event_frequency"],
                                              app["correlation"],
                                              self.stream_fps,
                                              observed_fps)

            fnrs.append(false_neg_rate)
            fprs.append(false_pos_rate)

            observed_unit = Schedule.ScheduleUnit(app,
                                                  observed_fps,
                                                  num_frozen)
            observed_schedule.append(observed_unit)

        observed_cost = scheduler_util.get_cost_schedule(observed_schedule,
                                                         self.model.layer_latencies,
                                                         self.model.final_layer)
        average_fnr = sum(fnrs) / float(len(fnrs))
        average_fpr = sum(fprs) / float(len(fprs))
        return round(average_fnr, 4), round(average_fpr, 4), round(observed_cost, 4)

    def get_cost_threshold(self, streamer_schedule, fpses):
        print "[get_cost_threshold] Recalculating..."
        fps_by_app_id = self.get_fps_by_app_id(streamer_schedule, fpses)
        observed_schedule = []
        for unit in self.schedule:
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
        if abs(target_cost - observed_cost) / target_cost < 0.20:
            return -1
        return observed_cost

    def run(self, cost_threshold, no_sharing = False, max_sharing = False):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        print "[Scheduler.run] Optimization function: %s" % (self.metric)

        if no_sharing:
            print "[Scheduler.run] Running no sharing model"
            self.num_frozen_list = [min(app["accuracies"].keys()) \
                                        for app in self.apps]

            # Get streamer schedule
            sched = self.make_streamer_schedule_no_sharing()
            #pp.pprint(sched)

            # Deploy schedule
            socket.send_json(sched)
            fps_message = socket.recv()
            fpses = fps_message.split(",")
            fpses = [float(fps) for fps in fpses]
            avg_rel_accs = 0

        elif max_sharing:
            print "[Scheduler.run] Running max sharing model"

            target_metric = self.set_max_parameters()

            # Get streamer schedule
            sched = self.make_streamer_schedule()

            # Deploy schedule
            socket.send_json(sched)
            fps_message = socket.recv()
            fpses = fps_message.split(",")
            fpses = [float(fps) for fps in fpses]

            avg_rel_accs = sum(self.get_relative_accuracies()) \
                            / float(len(self.get_relative_accuracies()))

        else:
            while cost_threshold > 0:
                # Get parameters
                print "[Scheduler.run] Optimizing with cost:", cost_threshold
                target_metric = self.optimize_parameters(cost_threshold)

                print "[Scheduler.run] Target metric:", target_metric

                # Get streamer schedule
                sched = self.make_streamer_schedule()

                # Deploy schedule
                socket.send_json(sched)
                fps_message = socket.recv()
                fpses = fps_message.split(",")
                fpses = [float(fps) for fps in fpses]

                cost_threshold = self.get_cost_threshold(sched, fpses)
                avg_rel_accs = sum(self.get_relative_accuracies()) \
                                / float(len(self.get_relative_accuracies()))

        observed_fnr, observed_fpr, observed_cost = self.get_observed_performance(sched,
                                                                                  fpses)

        return observed_fnr, observed_fpr, observed_cost, avg_rel_accs, self.num_frozen_list, fpses
