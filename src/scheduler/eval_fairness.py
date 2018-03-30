import random
import argparse
import sys
sys.path.append('data')
import app_data_mobilenets as app_data
sys.path.append('src/scheduler/types')
import Scheduler
import Schedule
import scheduler_util
import run_scheduler_simulator as sim
import os
import pickle


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-n", "--num_apps_range", required=True, type=int)
    # parser.add_argument("-b", "--budget_range", required=True, type=int)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-b", "--budget", default=300, type=int)
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names,
                                                       required=True,
                                                       help='provide at least one dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    # parser.add_argument("-r", "--run_id", required=True)
    parser.add_argument("-v", "--verbose", type=int, default=0)
    parser.add_argument("-r", "--metric-rescale", default=None, choices=[None, 'ratio_nosharing'])
    parser.add_argument("-x", "--x-vote", type=int, default=None)
    parser.add_argument("-s", "--scheduler", default="hifi")
    parser.add_argument("-i", "--input", nargs='+')
    return parser.parse_args()



def main():
    random.seed(1337)
    args = get_args(simulator=True)
    all_apps = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    x_vote = args.x_vote
    min_metric = args.metric

    # if x_vote is not None:
    #     outfile = args.outfile_prefix + "-x" + str(x_vote) + "-mainstream-simulator"
    #     min_metric += "-x"
    # else:
    #     outfile = args.outfile_prefix + "-mainstream-simulator"

    # Select app combinations.
    all_apps = [app_data.apps_by_name[app_name] for app_name in args.datasets]

    app_combs = sim.apps_hybrid(all_apps, args.num_apps_range)
    # Run simulator and do logging.
    # with open(outfile, "a+", 0) as f:
        # writer = csv.writer(f)


    results = []
    for filename in args.input:
        run_id = os.path.basename(filename).replace("-mainstream-simulator", "")
        with open(filename) as f:
            lines = [line.strip().split(',') for line in f]
            lines = [{'num_apps': int(line[0]), 'stats': map(float, line[1:4]), 'sharing': map(int, line[4:4+int(line[0])]), 'fps': map(int, line[4+int(line[0]):])} for line in lines]
            results.append((run_id, lines))


    att = {}
    for entry_id, app_ids in app_combs:
        apps = sim.apps_from_ids(app_ids, all_apps, x_vote)
        att[len(apps)] = [apps, run_simulator(min_metric, apps, budget=args.budget, verbose=args.verbose, scheduler=args.scheduler, metric_rescale=args.metric_rescale)]


    saved = []
    for run_id, lines in results:
        print run_id
        seen = {}
        for line in lines:
            at = att[line['num_apps']]
            print 'num_apps:', line['num_apps']
            cost_benefits, s = at[1]
            apps = at[0]
            app_stats = []
            configs = []
            schedule = []
            for i, (app, fps, num_frozen) in enumerate(zip(apps, line['fps'], line['sharing'])):
                cost, benefit = cost_benefits[i][num_frozen][fps]
                schedule.append(Schedule.ScheduleUnit(app, fps, num_frozen))
                # assert 0 <= benefit <= 1, benefit
                f1 = 1. - benefit
                configs.append((num_frozen, fps))
                app_stats.append([cost, benefit, f1])
            total_cost = scheduler_util.get_cost_schedule(schedule, s.model.layer_latencies, s.model.final_layer)
            f1s = [x[2] for x in app_stats]
            costs = [x[0] for x in app_stats]
            idd = (run_id, line['num_apps'])
            if idd in seen:
                print 'skipping'
                # assert seen[idd] == sum(f1s)/len(f1s)
                assert seen[idd] == f1s, (run_id, line['num_apps'])
            else:
                saved.append([run_id, line['num_apps'], f1s, costs, configs, line, app_stats, total_cost])
                seen[idd] = f1s
            print 'total cost:', total_cost
            print 'configs:'
            print '\t\t'.join(str(config) for config in configs)
            print 'F1s:'
            print '\t'.join(map('{:g}'.format, f1s))
            print 'min:', min(f1s)
            print 'max:', max(f1s)
            print 'mean:', sum(f1s)/len(f1s)
            print
        print

    pickle.dump([results, saved], open(args.outdir, 'wb'))


def run_simulator(min_metric, apps, budget=350, metric_rescale=None, **kwargs):
    s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                            app_data.model_desc, 0, **kwargs)
    return s.get_cost_benefits(budget, metric_rescale=metric_rescale), s

    # stats = {
    #     "metric": s.optimize_parameters(budget),
    #     "rel_accs": s.get_relative_accuracies(),
    # }

    # # Get streamer schedule
    # sched = s.make_streamer_schedule()

    # # Use target_fps_str in simulator to avoid running on the hardware
    # stats["fnr"], stats["fpr"], stats["f1"], stats["cost"] = s.get_observed_performance(sched, s.target_fps_list)
    # stats["fps"] = s.target_fps_list
    # stats["frozen"] = s.num_frozen_list
    # stats["avg_rel_acc"] = np.average(stats["rel_accs"])
    # return s, stats

# def get_args(simulator=True):
#     parser = argparse.ArgumentParser()
#     parser.add_argument("num_apps_range", type=int, help='1 to N for non-combs, just N for combs [for easier parallelism]')
#     parser.add_argument("outfile_prefix")
#     if not simulator:
#         parser.add_argument("-s", "--versions", nargs='+', default=["nosharing", "maxsharing"],
#                             choices=["mainstream", "nosharing", "maxsharing"])
#         parser.add_argument("-t", "--trials", default=1, type=int)
#     app_names = [app["name"] for app in app_data.app_options]
#     parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide one or multiple dataset names')
#     parser.add_argument("--scheduler", choices=['greedy', 'exhaustive', 'dp', 'hifi'], help='TODO: remove')
#     parser.add_argument("-m", "--metric", default="f1")
#     parser.add_argument("-a", "--agg", default="avg", choices=['avg', 'min'])
#     parser.add_argument("-b", "--budget", default=350, type=int)
#     parser.add_argument("-v", "--verbose", default=0, type=int)
#     parser.add_argument("-x", "--x-vote", type=int, default=None)
#     # For combinations
#     parser.add_argument("-c", "--combs", action='store_true')
#     parser.add_argument("--combs-no-shuffle", action='store_true')
#     parser.add_argument("-n", "--combs-dry-run", action='store_true')
#     parser.add_argument("--combs-max-samples", type=int)
#     return parser.parse_args()


if __name__ == '__main__':
    main()