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
sys.path.append('src/util')
import mpackage
#import app_data_mobilenets as app_data
import numpy as np


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps_range", type=int, help='1 to N for non-combs, just N for combs [for easier parallelism]')
    parser.add_argument("outfile_prefix")
    if not simulator:
        parser.add_argument("-s", "--versions", nargs='+', default=["nosharing", "maxsharing"],
                            choices=["mainstream", "nosharing", "maxsharing"])
        parser.add_argument("-t", "--trials", default=1, type=int)
    app_names = ["flowers", "cars", "cats", "pedestrian", "train", "bus", "redcar", "scramble", "schoolbus"]
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide one or multiple dataset names')
    parser.add_argument("--mode", default="mainstream", help="mainstream, nosharing or maxsharing")
    parser.add_argument("--scheduler", choices=['greedy', 'exhaustive', 'dp', 'hifi', 'stems', 'eq'])
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-a", "--agg", default="avg", choices=['avg', 'min'])
    parser.add_argument("-b", "--budget", default=350, type=int)
    parser.add_argument("-v", "--verbose", default=0, type=int)
    parser.add_argument("-x", "--x-vote", type=int, default=None)
    # For combinations
    parser.add_argument("-c", "--combs", action='store_true')
    parser.add_argument("--combs-no-shuffle", action='store_true')
    parser.add_argument("-n", "--combs-dry-run", action='store_true')
    parser.add_argument("--combs-max-samples", type=int)
    parser.add_argument("--curve-name", default="pedestrian-mobilenets")
    parser.add_argument("--curve-adjustment", default=0.0, type=float)
    return parser.parse_args()

args = get_args(simulator=True)

pedestrian_correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio
train_correlation_coefficient = .125 # Derived from train dataset, get_cp_ratio
correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio

def get_cp(acc, correlation_coefficient):
    delta_opt = acc
    cp = (1 - acc) + delta_opt * correlation_coefficient
    return cp

model_paths = {0:"flowers-mobilenet-80-frozen.pb",
               3:"flowers-mobilenet-80-frozen.pb",
               9:"flowers-mobilenet-80-frozen.pb",
               15:"flowers-mobilenet-80-frozen.pb",
               21:"flowers-mobilenet-80-frozen.pb",
               27:"flowers-mobilenet-80-frozen.pb",
               33:"flowers-mobilenet-80-frozen.pb",
               39:"flowers-mobilenet-80-frozen.pb",
               45:"flowers-mobilenet-80-frozen.pb",
               51:"flowers-mobilenet-80-frozen.pb",
               57:"flowers-mobilenet-80-frozen.pb",
               63:"flowers-mobilenet-80-frozen.pb",
               69:"flowers-mobilenet-80-frozen.pb",
               75:"flowers-mobilenet-80-frozen.pb",
               81:"flowers-mobilenet-80-frozen.pb",
               84:"flowers-mobilenet-80-frozen.pb"}

# Accuracy curve files
print os.path.dirname(__file__)
curves_dir = os.path.join(os.path.dirname(__file__), "../../data/mpackages")
curves = {
        "flowers": os.path.join(curves_dir, "flowers-mobilenets"),
        "cars": os.path.join(curves_dir, "cars-mobilenets"),
        "cats": os.path.join(curves_dir, "cats-mobilenets"),
        "pedestrian": os.path.join(curves_dir, args.curve_name),
        "train": os.path.join(curves_dir, "trains-mobilenets"),
        "bus": os.path.join(curves_dir, "bus-mobilenets"),
        "redcar": os.path.join(curves_dir, "redcar-mobilenets"),
        "scramble": os.path.join(curves_dir, "scramble-mobilenets"),
        "schoolbus": os.path.join(curves_dir, "schoolbus-mobilenets"),
        }

pedestrian_app = {"accuracies": mpackage.get_accuracy_curve(curves["pedestrian"], adjustment=args.curve_adjustment)[0],
                  "prob_tnrs" : mpackage.get_accuracy_curve(curves["pedestrian"])[1],
                  "event_length_ms": 500,
                  "event_frequency": 0.3,
                  "correlation_coefficient": pedestrian_correlation_coefficient,
                  "model_path": model_paths,
                  "name": "pedestrian"}

train_app = {"accuracies": mpackage.get_accuracy_curve(curves["train"])[0],
             "prob_tnrs" : mpackage.get_accuracy_curve(curves["train"])[1],
             "event_length_ms": 500,
             "event_frequency": 0.0138,
             "correlation_coefficient": train_correlation_coefficient,
             "model_path": model_paths,
             "name": "train"}

cars_app = {"accuracies": mpackage.get_accuracy_curve(curves["cars"])[0],
            "prob_tnrs" : mpackage.get_accuracy_curve(curves["cars"])[1],
            "event_length_ms": 500,
            "event_frequency": 0.5,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cars"}

cats_app = {"accuracies": mpackage.get_accuracy_curve(curves["cats"])[0],
            "prob_tnrs" : mpackage.get_accuracy_curve(curves["cats"])[1],
            "event_length_ms": 500,
            "event_frequency": 0.3,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cats"}

flowers_app = {"accuracies": mpackage.get_accuracy_curve(curves["flowers"])[0],
               "prob_tnrs" : mpackage.get_accuracy_curve(curves["flowers"])[1],
               "event_length_ms": 500,
               "event_frequency": 0.2,
               "correlation_coefficient": correlation_coefficient,
               "model_path": model_paths,
               "name": "flowers"}

bus_app = {"accuracies": mpackage.get_accuracy_curve(curves["bus"])[0],
           "prob_tnrs" : mpackage.get_accuracy_curve(curves["bus"])[1],
           "event_length_ms": 500,
           "event_frequency": 0.2,
           "correlation_coefficient": correlation_coefficient,
           "model_path": model_paths,
           "name": "bus"}

schoolbus_app = {"accuracies": mpackage.get_accuracy_curve(curves["schoolbus"])[0],
                 "prob_tnrs" : mpackage.get_accuracy_curve(curves["schoolbus"])[1],
                 "event_length_ms": 500,
                 "event_frequency": 0.2,
                 "correlation_coefficient": correlation_coefficient,
                 "model_path": model_paths,
                 "name": "schoolbus"}

redcar_app = {"accuracies": mpackage.get_accuracy_curve(curves["redcar"])[0],
              "prob_tnrs" : mpackage.get_accuracy_curve(curves["redcar"])[1],
              "event_length_ms": 500,
              "event_frequency": 0.2,
              "correlation_coefficient": correlation_coefficient,
              "model_path": model_paths,
              "name": "redcar"}

scramble_app = {"accuracies": mpackage.get_accuracy_curve(curves["scramble"])[0],
                "prob_tnrs" : mpackage.get_accuracy_curve(curves["scramble"])[1],
                "event_length_ms": 500,
                "event_frequency": 0.2,
                "correlation_coefficient": correlation_coefficient,
                "model_path": model_paths,
                "name": "scramble"}

app_options = [
               pedestrian_app,
               train_app,
               cars_app,
               flowers_app,
               cats_app,
               bus_app,
               schoolbus_app,
               scramble_app,
               redcar_app
               ]

apps_by_name = {app["name"]: app for app in app_options}

mobilenets_layer_latencies = [1.0, 1.0, 1.0, 0.8685, 0.8685, 0.8685, 0.8685,
        0.8685, 0.8685, 0.4863, 0.4863, 0.4863, 0.4863, 0.4863, 0.4863, 0.6383,
        0.6383, 0.6383, 0.6383, 0.6383, 0.6383, 0.3557, 0.3557, 0.3557, 0.3557,
        0.3557, 0.3557, 0.2155, 0.2155, 0.2155, 0.2155, 0.2155, 0.2155, 0.0248,
        0.0248, 0.0248, 0.0248, 0.0248, 0.0248, 0.0378, 0.0378, 0.0378, 0.0378,
        0.0378, 0.0378, 0.0373, 0.0373, 0.0373, 0.0373, 0.0373, 0.0373, 0.0594,
        0.0594, 0.0594, 0.0594, 0.0594, 0.0594, 0.0497, 0.0497, 0.0497, 0.0497,
        0.0497, 0.0497, 0.0428, 0.0428, 0.0428, 0.0428, 0.0428, 0.0428, 0.0626,
        0.0626, 0.0626, 0.0626, 0.0626, 0.0626, 0.083, 0.083, 0.083, 0.083,
        0.083, 0.083, 0.0109, 0.0109, 0.0109, 0.0109]

model_desc = {"total_layers": 85,
              "channels": 1,
              "height": 224,
              "width": 224,
              "layer_latencies": mobilenets_layer_latencies,
              "frozen_layer_names": {1:"input_1",
                                     3:"conv1_relu/clip_by_value",
                                     9:"conv_pw_1_relu/clip_by_value",
                                     15:"conv_pw_2_relu/clip_by_value",
                                     21:"conv_pw_3_relu/clip_by_value",
                                     27:"conv_pw_4_relu/clip_by_value",
                                     33:"conv_pw_5_relu/clip_by_value",
                                     39:"conv_pw_6_relu/clip_by_value",
                                     45:"conv_pw_7_relu/clip_by_value",
                                     51:"conv_pw_8_relu/clip_by_value",
                                     57:"conv_pw_9_relu/clip_by_value",
                                     63:"conv_pw_10_relu/clip_by_value",
                                     69:"conv_pw_11_relu/clip_by_value",
                                     75:"conv_pw_12_relu/clip_by_value",
                                     81:"conv_pw_13_relu/clip_by_value",
                                     84:"dense1/Relu",
                                     85:"dense_2/Softmax:0"}}

video_desc = {"stream_fps": 15}


def main():
    random.seed(1337)
    args = get_args(simulator=True)
    all_apps = [apps_by_name[app_name] for app_name in args.datasets]
    x_vote = args.x_vote
    min_metric = args.metric

    if x_vote is not None:
        outfile = args.outfile_prefix + "-x" + str(x_vote) + "-simulator"
        min_metric += "-x"
    else:
        outfile = args.outfile_prefix + "-simulator"

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
        for _, app_ids in app_combs:
            entry_id = len(app_ids)
            apps = apps_from_ids(app_ids, all_apps, x_vote)
            s, stats = run_simulator(min_metric,
                                     apps,
                                     video_desc,
                                     budget=args.budget,
                                     dp=dp,
                                     mode=args.mode,
                                     verbose=args.verbose,
                                     scheduler=args.scheduler,
                                     agg=args.agg)
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


def run_simulator(min_metric, apps, video_desc, budget=350, mode="mainstream", dp={}, **kwargs):
    s = Scheduler.Scheduler(min_metric, apps, video_desc,
                            model_desc, **kwargs)

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
