import argparse
import csv
from itertools import combinations, combinations_with_replacement
import os
import pprint as pp
import random
import time
import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import numpy as np


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps", type=int, help='Total number of apps to run')
    parser.add_argument("ratio_skip", type=int, help='1 to num_apps, must divide num_apps')
    parser.add_argument("outfile_prefix")
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide exactly two dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    # For combinations
    return parser.parse_args()


def main():
    random.seed(1337)
    args = get_args()
    app_datasets = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    min_metric = args.metric

    outfile = args.outfile_prefix + "-mainstream-simulator"

    # Run simulator and do logging.
    with open(outfile, "a+", 0) as f:
        writer = csv.writer(f)
        for num_first in range(0,args.num_apps+1,args.ratio_skip):
            print "{} {}, {} {}".format(num_first, args.datasets[0], args.num_apps - num_first, args.datasets[1])
            apps = get_combs(app_datasets, args.num_apps, num_first)
            s, stats = run_simulator(min_metric, apps)
            writer.writerow(get_eval(num_first, s, stats))
            f.flush()


def get_combs(app_datasets, num_apps, num_first):
    all_apps = []
    for i in range(0,num_first):
        app = app_datasets[0].copy()
        app["app_id"] = i
        all_apps.append(app)
    for i in range(num_first, num_apps):
        app = app_datasets[1].copy()
        app["app_id"] = i
        all_apps.append(app)
        
    return all_apps


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
    stats["fnr"], stats["fpr"], stats["cost"] = s.get_observed_performance(sched, s.target_fps_list)
    stats["fps"] = s.target_fps_list
    stats["frozen"] = s.num_frozen_list
    stats["avg_rel_acc"] = np.average(stats["rel_accs"])
    return s, stats


def get_eval(entry_id, s, stats):
    stats["recall"] = 1. - stats["fnr"]
    stats["precision"] = 1. - stats["fpr"]
    stats["f1"] = 2. / (1. / stats["recall"] + 1. / stats["precision"])
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
