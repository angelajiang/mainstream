import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import pprint as pp
import numpy as np
import time
import zmq
from itertools import combinations, combinations_with_replacement
import click
import os
import csv
import random
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('num_apps_range', type=int)
    parser.add_argument('x_vote', type=int, default=0)
    parser.add_argument('outfile')
    parser.add_argument('--agg', default='mean', help='agg (mean, min)')
    parser.add_argument('-m', '--metric', default='f1')
    parser.add_argument('-f', '--fairness', action='store_true')

    args = parser.parse_args()
    num_apps_range = args.num_apps_range
    x_vote = args.x_vote
    outfile = args.outfile + '-mainstream-simulator'
    min_metric = args.metric
    fairness = args.fairness
    agg = args.agg

    if agg == 'min':
        agg_func = np.min
    else:
        agg_func = np.average
    print agg, agg_func

    with open(outfile, "wb", 0) as f:
        for num_apps in range(len(app_data.app_options), \
                              num_apps_range+1,          \
                              len(app_data.app_options)):
            # Get Schedule
            apps = []

            for i in range(1, num_apps + 1):
                index = i % len(app_data.app_options)
                app = dict(app_data.app_options[index])
                app["app_id"] = i
                app["x_vote"] = x_vote
                apps.append(app)

            s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                                    app_data.model_desc, 0)

            metrics = s.optimize_per_app(350)
            avg_metric = sum(metrics) / len(metrics)
            rel_accs = s.get_relative_accuracies()
            avg_rel_acc = agg_func(rel_accs)
            print 'Rel accs: ', rel_accs
            print 'FNRs:', s.metrics
            print "Agg: {}, Num Apps: {}, FNR: {}, Avg Rel Acc: {}, Frozen: {}, FPS: {}".format(agg, num_apps, avg_metric, avg_rel_acc, s.num_frozen_list, s.target_fps_list)

            row = [
                str(num_apps),
                str(round(avg_metric, 4)),
                str(round(avg_rel_acc, 4)),
                "_".join(map(str, s.metrics)),
                "_".join(map(str, rel_accs)),
            ]
            line = ",".join(row) + "\n"
            f.write(line)
