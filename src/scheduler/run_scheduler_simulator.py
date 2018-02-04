import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import pprint as pp
import numpy as np
import time
import zmq
import argparse
import csv
import random
import os
from itertools import combinations, combinations_with_replacement


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps_range", type=int, help='1 to N for non-combs, just N for combs [for easier parallelism]')
    parser.add_argument("x_vote", type=int, default=0)
    parser.add_argument("outfile_prefix")
    parser.add_argument("-m", "--metric", default="f1")
    # For combinations
    parser.add_argument("-c", "--combs", action='store_true')
    parser.add_argument("-s", "--combs-no-shuffle", action='store_true')
    parser.add_argument("-n", "--combs-dry-run", action='store_true')
    parser.add_argument("--combs-max-samples", type=int)
    args = parser.parse_args()
    num_apps_range = args.num_apps_range
    x_vote = args.x_vote
    outfile_prefix = args.outfile_prefix
    min_metric = args.metric

    random.seed(1337)

    if x_vote > 0:
        outfile = outfile_prefix + "-x" + str(x_vote) + "-mainstream-simulator"
        min_metric += "-x"

    else:
        outfile = outfile_prefix + "-mainstream-simulator"

    # Select app combinations.
    all_apps = app_data.app_options

    if args.combs:
        app_combs = apps_combinations(all_apps, num_apps_range, outfile)
        if not args.combs_no_shuffle:
            random.shuffle(app_combs)

        if args.combs_max_samples is not None:
            app_combs = app_combs[:args.combs_max_samples]

        app_combs = remove_previous_combs(outfile, all_apps, app_combs)

        if args.combs_dry_run:
            for entry_id, _ in app_combs:
                print entry_id
            return
    else:
        app_combs = apps_hybrid(all_apps, num_apps_range)

    # Run simulator and do logging.
    with open(outfile, "a+", 0) as f:
        writer = csv.writer(f)
        for entry_id, app_ids in app_combs:
            apps = []
            for i, idx in enumerate(app_ids):
                app = dict(all_apps[idx])
                app["app_id"] = i
                app["x_vote"] = x_vote
                apps.append(app)

            s, stats = run_simulator(min_metric, apps)
            writer.writerow(get_eval(entry_id, s, stats))
            f.flush()


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


def run_simulator(min_metric, apps):
    s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                            app_data.model_desc, 0)

    metric = s.optimize_parameters(350)
    rel_accs = s.get_relative_accuracies()

    # Get streamer schedule
    sched = s.make_streamer_schedule()

    # Use target_fps_str in simulator to avoid running on the hardware
    fnr, fpr, cost = s.get_observed_performance(sched, s.target_fps_list)

    return s, [metric, fnr, fpr, rel_accs]


def get_eval(entry_id, s, stats):
    metric, fnr, fpr, rel_accs = stats
    avg_rel_acc = np.average(rel_accs)
    print "Metric:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
    print "FNR:", fnr, ", FPR:", fpr

    row = [
        entry_id,
        fnr,
        fpr,
        round(avg_rel_acc, 4),
    ]
    row += s.num_frozen_list
    row += s.target_fps_list
    return row


if __name__ == "__main__":
    main()
