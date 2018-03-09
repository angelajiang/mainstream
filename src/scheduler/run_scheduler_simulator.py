import argparse
import csv
from itertools import combinations, combinations_with_replacement
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
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-x", "--x-vote", type=int, default=None)
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

    if x_vote is not None:
        outfile = args.outfile_prefix + "-x" + str(x_vote) + "-mainstream-simulator"
        min_metric += "-x"
    else:
        outfile = args.outfile_prefix + "-mainstream-simulator"

    # Select app combinations.
    app_combs = get_combs(args, all_apps, args.num_apps_range, outfile)
    if app_combs is None:
        return
    # Run simulator and do logging.
    with open(outfile, "a+", 0) as f:
        writer = csv.writer(f)
        for entry_id, app_ids in app_combs:
            apps = apps_from_ids(app_ids, all_apps, x_vote)
            s, stats = run_simulator(min_metric, apps)
            writer.writerow(get_eval(entry_id, s, stats))
            f.flush()


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
        app_combs = apps_hybrid(all_apps, num_apps_range)
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


def run_simulator(min_metric, apps, budget=350):
    s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                            app_data.model_desc, 0)

    stats = {
        "metric": s.optimize_parameters(budget),
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
