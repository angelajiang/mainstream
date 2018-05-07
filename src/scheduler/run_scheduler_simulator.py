import argparse
import pickle
import dill
import csv
from itertools import combinations, combinations_with_replacement, product, chain
import os
import pprint as pp
import random
import time
import sys
sys.path.append('src/scheduler/types')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import numpy as np


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps_range", type=int, help='1 to N for non-combs, just N for combs [for easier parallelism]')
    parser.add_argument("outfile_prefix")
    if not simulator:
        parser.add_argument("-s", "--versions", nargs='+', default=["nosharing", "maxsharing"],
                            choices=["mainstream", "nosharing", "maxsharing"])
        parser.add_argument("-t", "--trials", default=1, type=int)
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide one or multiple dataset names')
    parser.add_argument("--scheduler", choices=['greedy', 'exhaustive', 'dp', 'hifi', 'stems'])
    parser.add_argument("--mode", default="mainstream", help="mainstream, nosharing or maxsharing")
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-a", "--agg", default="avg", choices=['avg', 'min'])
    parser.add_argument("-b", "--budget", default=350, type=int)
    parser.add_argument("-v", "--verbose", default=0, type=int)
    parser.add_argument("-x", "--x-vote", type=int, default=None)
    # Distributed
    parser.add_argument("--distributed-nodes", default=1, type=int)
    parser.add_argument("--saved-file", default=None)
    # For combinations
    parser.add_argument("-c", "--combs", action='store_true')
    parser.add_argument("--combs-no-shuffle", action='store_true')
    parser.add_argument("-n", "--combs-dry-run", action='store_true')
    parser.add_argument("--combs-max-samples", type=int)
    return parser.parse_args()


def main():
    random.seed(1337)
    args = get_args(simulator=True)
    all_apps = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    x_vote = args.x_vote
    min_metric = args.metric
    distributed_nodes = args.distributed_nodes
    save_file = args.saved_file
    if x_vote is not None:
        outfile = args.outfile_prefix + "-x" + str(x_vote) + "-mainstream-simulator"
        min_metric += "-x"
    else:
        outfile = args.outfile_prefix + "-mainstream-simulator"
    if distributed_nodes <= 0:
        print "Must select positive integer for number of nodes"
        return
    # Select app combinations.
    app_combs = get_combs(args, all_apps, args.num_apps_range, outfile)
    if app_combs is None:
        return
    # Run simulator and do logging.
    with open(outfile, "a+", 0) as f:
        writer = csv.writer(f)
        dp = None
        has_dp = not args.combs and (args.scheduler == "dp" or args.scheduler == "hifi")
        if has_dp:
            dp = {}
        print(app_combs)
        for entry_id, app_ids in app_combs:
            apps = apps_from_ids(app_ids, all_apps, x_vote)
            print "Simulating... " + str(len(apps))

            s, all_stats = run_simulator(min_metric,
                                     apps,
                                     app_data.video_desc,
                                     budget=args.budget,
                                     dp=dp,
                                     mode=args.mode,
                                     verbose=args.verbose,
                                     scheduler=args.scheduler,
                                     agg=args.agg,
                                     distributed_nodes=distributed_nodes,
                                     save_file=save_file)
            i = 1
            for stats in all_stats:
                writer.writerow(get_eval(i, s, stats))
                f.flush()
                i = i + 1


def get_combs(args, all_apps, num_apps_range, outfile):
    if args.combs:
        app_combs = apps_combinations(all_apps, num_apps_range, outfile)
        if not args.combs_no_shuffle:
            random.shuffle(app_combs)

        if args.combs_max_samples is not None:
            app_combs = app_combs[:args.combs_max_samples]

        app_combs = remove_previous_combs(outfile, all_apps, app_combs)

        if args.combs_dry_run:
            for entry_id, _ in app_combs:
                print(entry_id)
            return None
    else:
        # app_combs = apps_hybrid(all_apps, num_apps_range)
        app_combs = apps_hybrid_exact(all_apps, num_apps_range)
    return app_combs


def apps_from_ids(app_ids, all_apps, x_vote):
    apps = []
    for i, idx in enumerate(app_ids):
        app = dict(all_apps[idx])
        app["app_id"] = i
        if x_vote is not None:
            app["x_vote"] = x_vote
        apps.append(app)
    return apps


def remove_previous_combs(outfile, all_apps, combs):
    # Don't repeat combinations already tried.
    if os.path.isfile(outfile):
        with open(outfile) as f:
            reader = csv.reader(row for row in f if not row.startswith('#'))
            combs_done = [line[0].replace("mean=", "") for line in reader]
            combs = [(idx, c) for idx, c in combs if idx not in combs_done]
    return combs


def apps_combinations(all_apps, num_apps_range, outfile):
    combs = list(combinations_with_replacement(range(len(all_apps)), num_apps_range))
    entry_ids = ['_'.join(all_apps[app_id]['name'] for app_id in apps) for apps in combs]
    return list(zip(entry_ids, combs))


def apps_hybrid(all_apps, num_apps_range):
    app_combinations = []
    for num_apps in range(len(all_apps), \
                          num_apps_range+1,          \
                          len(all_apps)):
        app_combinations.append([i % len(all_apps)
                                 for i in range(1, num_apps + 1)])
    entry_ids = [len(apps) for apps in app_combinations]
    return list(zip(entry_ids, app_combinations))


def apps_hybrid_exact(all_apps, num_apps):
    return [(len(all_apps), [i % len(all_apps) for i in range(1, num_apps + 1)])]

def app_permutations(apps, distributed_nodes):
    partitions = []

    n = len(apps)
    all_partitions = list(product(range(distributed_nodes), repeat=n))
    for partition in all_partitions:
        assignments = []
        for node in range(distributed_nodes):
            assigned_to_node = frozenset([i for i,elem in enumerate(list(partition)) if elem == node])
            assignments.append(assigned_to_node)

        partitions.append(assignments)

    return partitions




def run_simulator(min_metric, apps, video_desc, budget=350, mode="mainstream", dp=None, agg='avg', distributed_nodes=1, save_file=None, **kwargs):
    total_start = time.time()
    app_indices = list(range(len(apps)))
    app_powerset = list(chain.from_iterable(combinations(app_indices, r) for r in range(len(app_indices)+1)))
    schedulers = dict()

    if os.path.isfile(save_file):
        with open(save_file, 'rb') as f:
            schedulers = pickle.load(f)
    else:

        for part in app_powerset:
            partition_start = time.time()
            part_set = frozenset(part)
            if len(part_set) == 0:
                stats = {
                    "metric": 0,
                    "rel_accs": [],
                    "fnr": 0,
                    "fpr": 0,
                    "f1": 0,
                    "cost": 0,
                    "fps": [],
                    "frozen": [],
                    "avg_rel_acc": 0,
                }
                schedulers[part_set] = (None, stats)
                continue

            part_apps_list = [apps[i] for i in part_set]
            print("Apps list: " + str(part_set))
    

            s = Scheduler.Scheduler(min_metric, part_apps_list, video_desc, app_data.model_desc, 0, **kwargs)
            stats = {
                "metric": s.optimize_parameters(budget, mode=mode, dp=dp),
                "rel_accs": s.get_relative_accuracies(),
            }
            sched = s.make_streamer_schedule()
    
            stats["fnr"], stats["fpr"], stats["f1"], stats["cost"] = s.get_observed_performance(sched, s.target_fps_list)
            stats["fps"] = s.target_fps_list
            stats["frozen"] = s.num_frozen_list
            stats["avg_rel_acc"] = np.average(stats["rel_accs"])

            schedulers[part_set] = (s, stats)
            partition_end = time.time()
            print("Subset time elapsed: " + str(partition_end - partition_start) + "\n")

        with open(save_file, 'wb') as f:
            pickle.dump(schedulers, f)

    all_stats = []
    for i in range(1,len(apps)+1):
        apps_i = apps[:i]

        partitions = app_permutations(apps_i, distributed_nodes)
    
        best_partition = None
        best_metric = -1
        for partition in partitions:
            if agg == 'min':
                met = -1
                for node in partition:
                    (node_s, node_stats) = schedulers[node]
                    if met == -1:
                        met = node_stats['metric']
                    else:
                        met = min(node_stats['metric'], met)
            else:
                met = 0
                for node in partition:
                    (node_s, node_stats) = schedulers[node]
                    print("Node: " + str(node) + ", F1: " + str(node_stats['f1']))
                    met = met + node_stats['metric'] * float(len(node)) / float(len(apps_i))

            if met < best_metric or best_metric == -1:
                best_metric = met
                best_partition = partition
            print("Best so far = F1: " + str(best_metric) + " for partition " + str(best_partition))

        # Aggregate stats for best partition
        stats = {
            "metric": best_metric
        }
        stats['fnr'] = 0
        stats['fpr'] = 0
        stats['f1'] = 0
        stats['cost'] = 0
        stats['fps'] = []
        stats['frozen'] = []
        stats['rel_accs'] = []

        for node in best_partition:
            (node_s, node_stats) = schedulers[node]
            stats['fnr'] = stats['fnr'] + node_stats['fnr'] * float(len(node)) / float(len(apps_i))
            stats['fpr'] = stats['fpr'] + node_stats['fpr'] * float(len(node)) / float(len(apps_i))
            stats['f1'] = stats['f1'] + node_stats['f1'] * float(len(node)) / float(len(apps_i))
            stats['cost'] = stats['cost'] + node_stats['cost'] * float(len(node)) / float(len(apps_i))
            stats['fps'] = stats['fps'] + node_stats['fps']
            stats['frozen'] = stats['frozen'] + node_stats['frozen']
            stats['rel_accs'] = stats['rel_accs'] + node_stats['rel_accs']

        stats['avg_rel_acc'] = np.average(stats['rel_accs'])
        all_stats.append(stats)
    total_end = time.time()
    print("Total time elapsed: " + str(total_end - total_start))
    return (None, all_stats)



    """
    s = Scheduler.Scheduler(min_metric, apps, video_desc, app_data.model_desc, 0, **kwargs)

    stats = {
        "metric": s.optimize_parameters(budget, mode=mode, dp=dp),
        "rel_accs": s.get_relative_accuracies(),
    }

    # Get streamer schedule
    sched = s.make_streamer_schedule()

    # Use target_fps_str in simulator to avoid running on the hardware
    stats["fnr"], stats["fpr"], stats["f1"], stats["cost"] = s.get_observed_performance(sched, s.target_fps_list)
    stats["fps"] = s.target_fps_list
    stats["frozen"] = s.num_frozen_list
    stats["avg_rel_acc"] = np.average(stats["rel_accs"])
    return s, stats
    """


def get_eval(entry_id, s, stats):
    stats["recall"] = 1. - stats["fnr"]
    stats["precision"] = 1. - stats["fpr"]
    if "metric" in stats:
        print "(Metric: {metric}, FNR: {fnr}, FPR: {fpr} \n \
                Recall: {recall:g}, Precision: {precision:g}, F1: {f1:g} \n \
                Frozen: {frozen}, FPS: {fps}, Cost: {cost}) ".format(**stats)
    else:
        print "(Observed FNR: {fnr}, FPR: {fpr} \n \
                Recall: {recall:g}, Precision: {precision:g}, F1: {f1:g} \n \
                Frozen: {frozen}, FPS: {fps}, Cost: {cost})".format(**stats)

    row = [
        entry_id,
        stats["fnr"],
        stats["fpr"],
        round(stats["avg_rel_acc"], 4),
    ]
    row += stats["frozen"]
    row += stats["fps"]
    return row


if __name__ == "__main__":
    main()
