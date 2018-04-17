import sys
sys.path.append('src/scheduler')
import scheduler_util
import Schedule
import itertools
import operator
import pprint as pp
import zmq
import math
from collections import Counter
import gc


class Scheduler:
    ### Object that performs optimization of parameters
    ### and feedback with Streamer

    def __init__(self, metric, apps, video_desc, model_desc, sigma, verbose=0, scheduler='greedy', agg='avg', metric_rescale=None):
        self.apps = apps
        self.video_desc = video_desc
        self.metric = metric
        self.model = Schedule.Model(model_desc)
        self.num_frozen_list = []
        self.target_fps_list = []
        self.sigma = sigma
        self.stream_fps = self.video_desc["stream_fps"]
        self.verbose = verbose
        self.scheduler = scheduler
        self.agg = agg
        self.metric_rescale = metric_rescale
        self._cost_benefits = None

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
            metric_by_schedule[tuple(schedule)] = round(avg_metric, 4)

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
            unit._metrics = self._get_all_metrics(app, num_frozen, target_fps)
            unit._metric = metric

            target_fps_list.append(target_fps)
            num_frozen_list.append(num_frozen)
            metrics.append(metric)

        average_metric = sum(metrics) / float(len(metrics))

        ## Print schedule
        metrics = ["f1", "recall", "precision", "fnr", "fpr"]
        xs = [""] + ["-x"+str(i+1) for i in range(2)]
        print "------------- Schedule -------------"
        for unit in schedule:
            print "App {}. Frozen: {}, FPS: {}, {}: {:g}".format(unit.app_id,
                                                                 unit.num_frozen,
                                                                 unit.target_fps,
                                                                 self.metric,
                                                                 1. - unit._metric),
            if self.verbose >= 1 and self._cost_benefits is not None:
                print ", cost: {:g}, benefit: {:g}".format(*self._cost_benefits[unit.app_id][unit.num_frozen][unit.target_fps])
            else:
                print
            if self.verbose >= 2:
                chosen_metric = self.metric
                if 'x_vote' in unit.app:
                    chosen_metric += str(unit.app['x_vote'])
                print "chosen_metric:", chosen_metric
                for x in xs:
                    output = "        "
                    def f(m):
                        a = "{}: {:g}".format(m+x, unit._metrics[m+x])
                        if chosen_metric == m+x:
                            return '*'+a
                        return a
                    output += ", ".join(f(m) for m in metrics)
                    print output
        print "Avg F1-score:", 1 - average_metric

        ## Set parameters of schedule
        self.schedule = schedule
        self.num_frozen_list = num_frozen_list
        self.target_fps_list = target_fps_list

        return average_metric

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

    def _get_all_metrics(self, app, num_frozen, target_fps):
        metrics = ["f1", "fnr", "fpr"]
        xs = [""] + ["-x"+str(i+1) for i in range(2)]
        results = {}
        for x in xs:
            for metric in metrics:
                kwargs = {}
                if "-x" in x:
                    kwargs['x_vote'] = int(x[2:])
                results[metric + x] = self._get_metric(app, num_frozen, target_fps, metric, **kwargs)
            results["f1"+x] = 1. - results["f1"+x]
            results["recall"+x] = 1. - results["fnr"+x]
            results["precision"+x] = 1. - results["fpr"+x]
        return results

    def get_metric(self, app, num_frozen, target_fps):
        # "self.metric" is metric to minimize. In set {"f1", "fnr", "fpr"}
        kwargs = {}
        metric_name = self.metric
        if metric_name.endswith('-x'):
            kwargs['x_vote'] = app["x_vote"]
            metric_name = metric_name[:-2]
        return self._get_metric(app, num_frozen, target_fps, metric_name, **kwargs)

    def _get_metric(self, app, num_frozen, target_fps, metric_name, **kwargs):
        accuracy = app["accuracies"][num_frozen]
        if metric_name == "f1":
            prob_tnr = app["prob_tnrs"][num_frozen]
            f1 = scheduler_util.get_f1_score(accuracy,
                                             prob_tnr,
                                             app["event_length_ms"],
                                             app["event_frequency"],
                                             app["correlation_coefficient"],
                                             self.stream_fps,
                                             target_fps,
                                             **kwargs)
            metric = 1 - f1
        elif metric_name == "fnr":
            metric = scheduler_util.get_false_neg_rate(accuracy,
                                                       app["event_length_ms"],
                                                       app["correlation_coefficient"],
                                                       self.stream_fps,
                                                       target_fps,
                                                       **kwargs)
        elif metric_name == "fpr":
            prob_tnr = app["prob_tnrs"][num_frozen]
            metric = scheduler_util.get_false_pos_rate(
                                              accuracy,
                                              prob_tnr,
                                              app["event_length_ms"],
                                              app["event_frequency"],
                                              app["correlation_coefficient"],
                                              self.stream_fps,
                                              target_fps,
                                              **kwargs)
        else:
            raise Exception("Didn't recognize metric {}. Exiting.".format(metric_name))
        return metric

    def _get_num_frozen_options(self, app, mode):
        all_num_frozen = sorted(app["accuracies"].keys())
        if mode == "mainstream":
            return all_num_frozen
        elif mode == "nosharing":
            return [min(all_num_frozen)]
        elif mode == "maxsharing":
            return [max(all_num_frozen)]
        else:
            raise Exception("Didn't recognize mode {}. Exiting.".format(mode))

    def _get_target_fps_options(self, mode):
        target_fps_ints = range(1, self.stream_fps + 1)
        if mode == "mainstream":
            return target_fps_ints
        elif mode == "nosharing":
            target_fps_floats = [i * 0.1 for i in range(1, 10)]
            return target_fps_floats + target_fps_ints
        elif mode == "maxsharing":
            return target_fps_ints
        else:
            raise Exception("Didn't recognize mode {}. Exiting.".format(mode))

    def get_cost_benefits(self,
                          mode="mainstream",
                          cost_threshold=None,
                          metric_rescale=None):
        cost_benefits = {}
        target_fps_options = self._get_target_fps_options(mode)

        if metric_rescale == "ratio_nosharing":
            per_app_budget = cost_threshold / float(len(self.apps))
            per_app_fps = per_app_budget / sum(self.model.layer_latencies)
            print "per app budget, FPS:", per_app_budget, per_app_fps

        for app in self.apps:
            app_id = app["app_id"]
            cost_benefits[app_id] = {}
            num_frozen_options = self._get_num_frozen_options(app, mode)
            for num_frozen in reversed(sorted(num_frozen_options)):
                if num_frozen not in cost_benefits[app_id]:
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

            if metric_rescale == "ratio_nosharing":
                flattened = {(num_frozen, target_fps): cost_benefit_tup
                             for num_frozen, dct in cost_benefits[app_id].items()
                             for target_fps, cost_benefit_tup in dct.items()}

                def get_stem_cost(num_frozen, fps):
                    return sum(self.model.layer_latencies[i] for i in range(num_frozen)) * fps

                grid = [benefit for (num_frozen, fps), (cost, benefit) in flattened.items() if get_stem_cost(num_frozen, fps) + cost <= per_app_budget]
                # Consider FPS < 1 as well
                min_num_frozen = min(app["accuracies"].keys())
                grid.append(self.get_metric(app, min_num_frozen, per_app_fps))
                best_benefit = min(grid)
                print 'Best benefit:', best_benefit
                # print 'Before:', cost_benefits[app_id]
                for num_frozen, dct in cost_benefits[app_id].items():
                    cost_benefits[app_id][num_frozen] = {target_fps: (cost, benefit / best_benefit)
                                                         for target_fps, (cost, benefit) in dct.items()}
                # print 'After:', cost_benefits[app_id]
             # TODO: Rebase
             # TODO: Rescale
        self._cost_benefits = cost_benefits
        return cost_benefits

    def get_init_agg_func(self, agg=None):
        agg = agg or self.agg
        func_init = lambda x: (x, x)
        if self.agg == 'avg':
            agg_func = lambda x, y: (x[0] + y[0], min(x[1], y[1]))
        elif self.agg == 'min':
            # for max-min
            agg_func = lambda x, y: (min(x[0], y[0]), x[1] + y[1])
        else:
            raise Exception("Unknown agg func {}".format(self.agg))
        return func_init, agg_func

    def hifi_scheduler(self, cost_threshold, mode, dp={}):
        cost_benefits = self.get_cost_benefits(
            mode=mode,
            cost_threshold=cost_threshold,
            metric_rescale=self.metric_rescale)
        print "Metric rescale: ", self.metric_rescale
        target_fps_options = self._get_target_fps_options(mode)

        func_init, agg_func = self.get_init_agg_func()

        dp = {}

        num_apps = 0
        if len(dp) > 0:
            num_apps = dp["num_apps"]

        dp_prev = dict(dp)

        def relax2(curr, best_by_budget, curr_cost, curr_goodness, c_unit, threshold):
            # curr/best_by_budget: [(benefit, min_cost), (benefit_lower, min_cost_lower)]
            vals = []
            for prev_goodness, prev_budget, info in reversed(best_by_budget):
                new_budget = prev_budget + curr_cost
                # Pruning
                if new_budget > threshold:
                    # Note: break depends on reversed, otherwise must be continue.
                    break
                new_goodness = agg_func(prev_goodness, curr_goodness)
                # new_budget = math.ceil(new_budget * 50) / 50.
                # new_goodness = int(new_goodness * 1000) / 1000.
                vals.append((new_goodness, new_budget, {'unit': c_unit, 'prev': info}))
            if len(curr) == 0:
                return vals
            elif len(vals) == 0:
                return curr
            ret = scheduler_util.merge_monotonic(curr, list(reversed(vals)))
            return ret

        for i, app in enumerate(self.apps):
            if i < num_apps:
                continue
            dp.clear()
            dp["num_apps"] = i+1
            dp_prev_only = {k: v for k, v in dp_prev.items() if k != "num_apps"}
            num_frozen_options = self._get_num_frozen_options(app, mode)

            for c_frozen in num_frozen_options:
                p_benefit = 0
                for c_fps in target_fps_options:
                    c_cost, c_benefit = cost_benefits[app["app_id"]][c_frozen][c_fps]
                    c_benefit = func_init(1. - c_benefit)
                    if c_benefit <= p_benefit:
                        break
                    p_benefit = c_benefit
                    c_unit = Schedule.ScheduleUnit(app, c_fps, c_frozen)
                    if i == 0:
                        stem = scheduler_util.SharedStem([(c_frozen, c_fps)], self.model)
                        assert stem not in dp
                        if stem.cost + c_cost <= cost_threshold:
                            dp[stem] = [(c_benefit, c_cost, {'unit': c_unit, 'prev': None})]
                    else:
                        for stem, best_by_budget in dp_prev_only.iteritems():
                            new_stem = stem.relax(c_frozen, c_fps)
                            assert new_stem.cost >= stem.cost
                            result = relax2(dp.get(new_stem, []), best_by_budget, c_cost, c_benefit, c_unit, cost_threshold - new_stem.cost)
                            if len(result) > 0:
                                dp[new_stem] = result

            if self.verbose > -1:
                print '{} apps'.format(i+1),

                dp_only = {k: v for k, v in dp.items() if k != "num_apps"}
                print 'Unique stems:', len(dp_only)
                lens_budgets_by_stem = map(len, dp_only.values())
                budgets_by_stem = Counter(lens_budgets_by_stem)
                print 'Total DP values', sum(lens_budgets_by_stem)
            if self.verbose > 1:
                budgets = [y[1] for x in dp_only.values() for y in x]
                goodnesses = [y[0] for x in dp_only.values() for y in x]
                cnt_budgets = Counter(budgets)
                cnt_goodness = Counter(goodnesses)
                def bucket_stats(vals):
                    ret = [Counter(map(int, vals))]
                    return ret + [Counter(map(lambda x: int(x * k) / k, vals)) for k in [10., 100., 1000., 10000.]]
                cnt_budgets_buckets = bucket_stats(budgets)
                cnt_goodness_buckets = bucket_stats(goodnesses)
                print 'Unique budgets:', len(cnt_budgets)
                print 'Budget buckets by int, .1, .01, .001:', map(len, cnt_budgets_buckets)
                print 'Unique goodness scores', len(cnt_goodness)
                print 'Goodness buckets by int, .1, .01, .001:', map(len, cnt_goodness_buckets)
                print 'Budgets per stem', budgets_by_stem
                # print 'Budgets:', ', '.join(map('{:.0f}'.format, sorted(cnt_budgets.keys(), reverse=True)))
                # print 'Budgets:', sorted(map(int, cnt_budgets.keys()), reverse=True)
                print 'Budgets by ints:', cnt_budgets_buckets[0]
                # print 'Some budgets:', map('{:g}'.format, sorted(cnt_budgets.keys()))
                # print 'Num of DP values by budget', sorted(cnt_budgets.values(), reverse=True)
                # print 'Num of DP values by goodness', sorted(cnt_goodness.values(), reverse=True)
                # print 'curr, vals:', cc
                cc.clear()
                print

            if i > 0:
                del dp_prev
            gc.collect()
            dp_prev = dp_only

        options = []
        for stem, best_by_budget in dp_prev.iteritems():
            options += [(goodness, budget + stem.cost, info) for goodness, budget, info in best_by_budget if budget + stem.cost <= cost_threshold]
        results = scheduler_util.make_monotonic(options)

        best_result = results[0]
        if self.verbose > 1:
            print 'Best:', best_result[:2]
        # best_schedule = best_result[2]['schedule']
        best_schedule = scheduler_util.extract_schedule(best_result[2])
        if self.verbose > 1:
            print 'Schedule cost:', scheduler_util.get_cost_schedule(best_schedule, self.model.layer_latencies, self.model.final_layer)
        avg_metric = self.set_schedule_values(best_schedule)
        return avg_metric

    def stems_scheduler(self, cost_threshold, mode):
        # Currently: brute forces all stems, runs DP for each stem individually
        #
        # run-time: O(# of stems * num_apps * budget * num_frozen * fps
        #
        # the last num_frozen * fps could probably be amortized but this might
        # be moot since # of stems grows ~O(num_frozen! fps!)
        cost_benefits = self.get_cost_benefits(
            mode=mode,
            cost_threshold=cost_threshold,
            metric_rescale=self.metric_rescale)
        target_fps_options = self._get_target_fps_options(mode)
        chokepoints = sorted(set(key for app in self.apps for key in self._get_num_frozen_options(app, mode)))

        func_init, agg_func = self.get_init_agg_func()

        best_result = None
        if self.verbose > 0:
            print "k_steps, total stems, total stems in budget, total stems that improved over prev optimal, ops, ops per stem, updates (ops that resulted in change)"
        for k in range(1, 1 + min((len(target_fps_options), len(chokepoints), len(self.apps)))):
            num_stems, num_stems_in_budget, stems_improved = 0, 0, 0
            ops = 0
            updates = 0
            for chosen_fpses in itertools.combinations(target_fps_options, k):
                chosen_fpses = list(reversed(chosen_fpses))
                for chosen_chokepoints in itertools.combinations(chokepoints, k):
                    stem = scheduler_util.SharedStem(zip(chosen_chokepoints, chosen_fpses), self.model)
                    num_stems += 1
                    if stem.cost > cost_threshold:
                        continue
                    num_stems_in_budget += 1
                    dp = {}
                    for i, app in enumerate(self.apps):
                        num_frozen_options = sorted(app["accuracies"].keys())
                        stem_ptr = 0
                        min_objective_by_budget = []
                        if i > 0:
                            prev_curve = list(reversed(dp[i-1]))
                        options_for_stem = []
                        for c_frozen in num_frozen_options:
                            # Find out max FPS supported by stem at c_frozen
                            while stem_ptr < len(stem) and stem.stem[stem_ptr][0] < c_frozen:
                                stem_ptr += 1
                            if stem_ptr >= len(stem):
                                break

                            for c_fps in target_fps_options:
                                # Assumes that target_fps_options is sorted
                                if c_fps > stem.stem[stem_ptr][1]:
                                    break
                                c_cost, c_benefit = cost_benefits[app["app_id"]][c_frozen][c_fps]
                                c_benefit = func_init(1. - c_benefit)
                                if stem.cost + c_cost > cost_threshold:
                                    break
                                c_unit = Schedule.ScheduleUnit(app, c_fps, c_frozen)
                                options_for_stem.append((c_benefit, c_cost, c_unit))

                        # Prune away options that are not optimal
                        options_for_stem_ = scheduler_util.make_monotonic(options_for_stem)

                        if i == 0:
                            for c_benefit, c_cost, c_unit in options_for_stem_:
                                min_objective_by_budget.append((c_benefit, c_cost + stem.cost, {'unit': c_unit, 'prev': None}))
                            scheduler_util.check_monotonic(min_objective_by_budget)
                        else:
                            options_for_stem_ = list(reversed(options_for_stem_))
                            curr_best = None
                            for ii, (prev_goodness, prev_budget, info) in enumerate(prev_curve):
                                if ii != len(prev_curve) - 1 and len(options_for_stem_) > 0:
                                    next_pt = prev_curve[ii+1]
                                    next_pt = (agg_func(next_pt[0], options_for_stem_[0][0]), next_pt[1] + options_for_stem_[0][1])
                                else:
                                    next_pt = None
                                for c_benefit, c_cost, c_unit in options_for_stem_:
                                    ops += 1
                                    new_budget = prev_budget + c_cost
                                    # Pruning
                                    if new_budget > cost_threshold:
                                        # Note: break depends on reversed, otherwise must be continue.
                                        break
                                    new_goodness = agg_func(prev_goodness, c_benefit)
                                    if curr_best is not None and curr_best >= (new_goodness, -new_budget):
                                        continue
                                    if next_pt is not None and next_pt[1] <= new_budget and next_pt[0] >= new_goodness:
                                        break
                                    curr_best = (new_goodness, -new_budget)
                                    min_objective_by_budget.append((new_goodness, new_budget, {'unit': c_unit, 'prev': info}))
                                    updates += 1

                            min_objective_by_budget = list(reversed(min_objective_by_budget))
                        dp[i] = scheduler_util.make_monotonic(min_objective_by_budget)

                    stem_sols = [(goodness, budget, info)
                                 for goodness, budget, info in dp[len(self.apps) - 1]
                                 if budget <= cost_threshold]
                    if len(stem_sols) > 0:
                        best_stem_sol = stem_sols[0]
                        if best_result is None or best_result[0] < best_stem_sol[0] or (best_result[0] == best_stem_sol[0] and best_result[1] > best_stem_sol[1]):
                            if self.verbose > 0:
                                print 'improved:', stem, best_stem_sol
                            stems_improved += 1
                            best_result = best_stem_sol
            # k_steps, total stems, total stems in budget, total stems that improved over prev optimal, ops, ops per stem, updates (ops that resulted in change)
            if self.verbose > 0:
                print k, num_stems, num_stems_in_budget, stems_improved, ops, ops / max(1, num_stems_in_budget), updates
        if self.verbose > 1:
            print 'Best:', best_result[:2]

        best_schedule = scheduler_util.extract_schedule(best_result[2])
        if self.verbose > 1:
            print 'Schedule cost:', scheduler_util.get_cost_schedule(best_schedule, self.model.layer_latencies, self.model.final_layer)
        avg_metric = self.set_schedule_values(best_schedule)
        return avg_metric

    def optimize_parameters(self, cost_threshold, mode="mainstream", dp=None):
        # Makes schedule with optimal choices for num_frozen and target_fps
        # Sets self.schedule, self.num_frozen_list, self.target_fps_list
        if self.scheduler == 'greedy':
            return self.greedy_scheduler(cost_threshold, mode)
        elif self.scheduler == 'dp':
            return self.dp_scheduler(cost_threshold, mode, dp=dp)
        elif self.scheduler == 'hifi':
            return self.hifi_scheduler(cost_threshold, mode, dp=dp)
        elif self.scheduler == 'stems':
            return self.stems_scheduler(cost_threshold, mode)
        else:
            raise Exception("Unknown scheduler {}".format(self.scheduler))

    def greedy_scheduler(self, cost_threshold, mode):
        cost_benefits = self.get_cost_benefits(
            mode=mode,
            cost_threshold=cost_threshold,
            metric_rescale=self.metric_rescale)
        target_fps_options = self._get_target_fps_options(mode)

        current_schedule = []
        for app in self.apps:
            num_frozen_options = self._get_num_frozen_options(app, mode)
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
                num_frozen_options = self._get_num_frozen_options(app, mode)
                cur_metric = cost_benefits[app_id][cur_num_frozen][cur_target_fps][1]

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
                        potential_metric = cost_benefit_tup[1]
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
        f1s = []
        observed_schedule = []
        for app, num_frozen in zip(self.apps, self.num_frozen_list):
            kwargs = {}
            if self.metric.endswith('-x'):
                kwargs['x_vote'] = app['x_vote']
            observed_fps = fps_by_app_id[app["app_id"]]

            accuracy = app["accuracies"][num_frozen]
            prob_tnr = app["prob_tnrs"][num_frozen]
            false_neg_rate = scheduler_util.get_false_neg_rate(
                                              accuracy,
                                              app["event_length_ms"],
                                              app["correlation_coefficient"],
                                              self.stream_fps,
                                              observed_fps,
                                              **kwargs)
            false_pos_rate = scheduler_util.get_false_pos_rate(
                                              accuracy,
                                              prob_tnr,
                                              app["event_length_ms"],
                                              app["event_frequency"],
                                              app["correlation_coefficient"],
                                              self.stream_fps,
                                              observed_fps,
                                              **kwargs)

            recall = 1. - false_neg_rate
            precision = 1. - false_pos_rate
            f1 = 2. / (1. / recall + 1. / precision)

            fnrs.append(false_neg_rate)
            fprs.append(false_pos_rate)
            f1s.append(f1)

            observed_unit = Schedule.ScheduleUnit(app,
                                                  observed_fps,
                                                  num_frozen)
            observed_schedule.append(observed_unit)

        observed_cost = scheduler_util.get_cost_schedule(observed_schedule,
                                                         self.model.layer_latencies,
                                                         self.model.final_layer)
        average_fnr = sum(fnrs) / float(len(fnrs))
        average_fpr = sum(fprs) / float(len(fprs))
        average_f1 = sum(f1s) / float(len(f1s))
        return round(average_fnr, 4), round(average_fpr, 4), round(average_f1, 4), round(observed_cost, 4)

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

    def run(self, cost_threshold, mode='mainstream'):
        ### Run function invokes scheduler and streamer feedback cycle

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        print "[Scheduler.run] Optimization function: %s" % (self.metric)

        if mode == 'nosharing':
            print "[Scheduler.run] Running no sharing model"
            self.num_frozen_list = [min(app["accuracies"].keys()) for app in self.apps]

            # Get streamer schedule
            sched = self.make_streamer_schedule_no_sharing()

            # Deploy schedule
            socket.send_json(sched)
            fps_message = socket.recv()
            fpses = fps_message.split(",")
            fpses = [float(fps) for fps in fpses]
            avg_rel_accs = 0

        elif mode == 'maxsharing':
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

        elif mode == 'mainstream':
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
        else:
            raise Exception("Unknown sharing setting {}".format(sharing))

        observed_fnr, observed_fpr, observed_f1, observed_cost = self.get_observed_performance(sched,
                                                                                               fpses)

        return observed_fnr, observed_fpr, observed_f1, observed_cost, avg_rel_accs, self.num_frozen_list, fpses
