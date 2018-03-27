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

randomize = True
initial_distribution = {'pedestrian': 2, 'train': 2, 'cats': 1, 'cars': 1}

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps", type=int, help='Total number of apps to run')
    parser.add_argument("outfile_prefix")
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("--scheduler", choices=['greedy', 'exhaustive', 'dp', 'hifi'], help='TODO: remove')
    parser.add_argument("-b", "--budget", default=350, type=int)
    parser.add_argument("-v", "--verbose", default=0, type=int)
    # For combinations
    return parser.parse_args()

def main():
    random.seed(1337)
    args = get_args()
#    app_datasets = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    min_metric = args.metric

    outfile = args.outfile_prefix + "-mainstream-simulator"

    # Run simulator and do logging.
    with open(outfile, "a+", 0) as f:
        writer = csv.writer(f)
        total_workload = initial_distribution.copy()
        for i in range(0,args.num_apps):
            for app_type in total_workload:
                total_workload[app_type] = total_workload[app_type] + initial_distribution[app_type]
            apps_list = []
            for app_type in total_workload:
                apps_list = apps_list + [app_data.apps_by_name[app_type]]*total_workload[app_type]

            if randomize:
                workload = randomize_load(apps_list)
            else:
                workload = user_defined_distribution(apps_list)

            w0 = len(workload[0])
            w1 = len(workload[1])

            wl_names = [[],[]]
            wl_names[0] = [a['name'] for a in workload[0]]
            wl_names[1] = [a['name'] for a in workload[1]]
        
            print("Node 0: " + str(wl_names[0]))
            print("Node 1: " + str(wl_names[1]))

            s0,stats0 = run_simulator(min_metric, workload[0], budget=args.budget, scheduler=args.scheduler, args=args)
            s1,stats1 = run_simulator(min_metric, workload[1], budget=args.budget, scheduler=args.scheduler, args=args)

            sc,statsc = combine_stats(s0,stats0,w0,s1,stats1,w1)

            writer.writerow(get_eval(i,sc,statsc))
            f.flush()
            

#        for num_first in range(0,args.num_apps+1,args.ratio_skip):
#            print "{} {}, {} {}".format(num_first, args.datasets[0], args.num_apps - num_first, args.datasets[1])
#            apps = get_combs(app_datasets, args.num_apps, num_first)
#            s, stats = run_simulator(min_metric, apps, app_data.video_desc, budget=args.budget, scheduler=args.scheduler,args=args)
#            writer.writerow(get_eval(num_first, s, stats))
#            f.flush()

def randomize_load(full_workload):
    workload = [[], []]
    i = 0
    for app in full_workload:
        a = app.copy()
        a["app_id"] = i
        workload[random.randint(0,1)].append(a)
        i+=1
    return workload

def user_defined_distribution(total_workload):
    workload = [[],[]]
    i = 0
    for a in total_workload:
        app = a.copy()
        app['app_id'] = i
        i+=1
        if app['name'] == 'cats':
            workload[0].append(app)
        else:
            workload[1].append(app)
    return workload




def get_combs_defined(nums_dict):
    all_apps = []
    for app in nums_dict:
        num_app = nums_dict[app]
        for i in range(0,num_app):
            a = app.copy()
            a["app_id"] = i
        all_apps.append(a)
    return all_apps


def get_combs_two_app(app_datasets, num_apps, num_first):
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


def run_simulator(min_metric, apps, budget=350, scheduler="greedy", verbose=False, args=None):
    s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                            app_data.model_desc, 0, verbose=verbose, scheduler=scheduler)

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

def combine_stats(s0, stats0, w0, s1, stats1, w1):
    statsc = stats0.copy()
    sc = dict()

    #To define: cost, rel_accs 

    statsc['fnr'] = stats0['fnr'] * w0 + stats1['fnr'] * w1
    statsc['fpr'] = stats0['fpr'] * w0 + stats1['fpr'] * w1
    statsc['frozen'] = min(stats0['frozen'], stats1['frozen'])
    statsc['fps'] = stats0['fps'] * w0 + stats1['fps'] * w1
    statsc['avg_rel_acc'] = stats0['avg_rel_acc'] * w0 + stats1['avg_rel_acc'] * w1

    return (s0, statsc)

if __name__ == "__main__":
    main()
