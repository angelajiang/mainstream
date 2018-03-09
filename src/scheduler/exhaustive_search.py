

import argparse
import csv
import fnmatch
import scheduler_util
import os
import sys
import app_data_mobilenets as app_data

sys.path.append('src/scheduler')
import run_scheduler_simulator as sim

sys.path.append('src/scheduler/types')
import Scheduler


VERSION_SUFFIX = ".v0"

# Directory structure
# outdir/
#   pointers.run_id.v0
#   setup/
#       configuration.config_suffix.v0
#       model.config_suffix.v0
#       environment.config_suffix.v0
#   schedules/
#       greedy.run_id.v0
#       exhaustive.run_id.v0

def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-n", "--num_apps_range", required=True, type=int)
    parser.add_argument("-b", "--budget_range", required=True, type=int)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names,
                                                       required=True,
                                                       help='provide at least one dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-r", "--run_id", required=True)
    parser.add_argument("-v", "--verbose", type=int, default=0)
    return parser.parse_args()


def get_eval(entry_id, s, stats, budget):
    row = [
        entry_id,
        stats["metric"],
    ]
    row += stats["frozen"]
    row += stats["fps"]
    row += [budget]
    return row


def write_cost_benefits_file(cost_benefits, outdir, filename):
    subdir = os.path.join(outdir, "setup");
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    outfile = os.path.join(subdir, "configuration." + filename)
    with open(outfile, "a+") as f:
        for app_id, d1 in cost_benefits.iteritems():
            for num_frozen, d2 in d1.iteritems():
                for target_fps, d3 in d2.iteritems():
                    cost = d3[0]
                    benefit = d3[1]
                    line = "{} {} {} {} {}\n".format(app_id,
                                                     num_frozen,
                                                     target_fps,
                                                     cost,
                                                     benefit)
                    f.write(line)
    return outfile


def write_model_file(layer_costs, outdir, filename):
    subdir = os.path.join(outdir, "setup");
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    outfile = os.path.join(subdir, "model." + filename)
    with open(outfile, "a+") as f:
        layer_costs_str = [str(c) for c in layer_costs]
        line = " ".join(layer_costs_str) + "\n"
        f.write(line)
    return outfile


def write_environment_file(budget, outdir, filename):
    subdir = os.path.join(outdir, "setup");
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    outfile = os.path.join(subdir, "environment." + filename)
    with open(outfile, "a+") as f:
        line = str(budget) + "\n"
        f.write(line)
    return outfile


def run(args, apps, budget, config_suffix):

    s = Scheduler.Scheduler(args.metric,
                            apps,
                            app_data.video_desc,
                            app_data.model_desc,
                            0)

    # Write cost benefits, model, and environment data for cpp fn
    cost_benefits = s.get_cost_benefits()
    f1 = write_cost_benefits_file(cost_benefits, args.outdir, config_suffix)
    f2 = write_model_file(s.model.layer_latencies, args.outdir, config_suffix)
    f3 = write_environment_file(budget, args.outdir, config_suffix)

    # Store filenames which point to schedule data
    # Each line represents one schedule-configuration
    pointers_file = os.path.join(args.outdir, "pointers." + args.run_id + VERSION_SUFFIX)
    with open(pointers_file, "a+") as f:
        line = "{}\n".format(config_suffix)
        f.write(line)
        f.flush()

    # Write output with mainstream-simulator schedules
    s, stats = sim.run_simulator(args.metric, apps, budget)

    subdir = os.path.join(args.outdir, "schedules");
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    outfile = os.path.join(subdir, "greedy." + args.run_id + VERSION_SUFFIX)

    with open(outfile, "a+") as f:
        writer = csv.writer(f)
        writer.writerow(get_eval(len(apps), s, stats, budget))
        f.flush()

    # Write debug output
    if (bool(args.verbose)):
        min_metric = 2
        print "[Warning] Trying to get all combos in python"
        schedules, metrics, costs = s.get_parameter_options();
        for schedule, metric, cost in zip(schedules, metrics, costs):
            if cost <= budget and metric < min_metric:

                num_frozen_list = [str(app.num_frozen) for app in schedule]
                fps_list = [str(app.target_fps) for app in schedule]
                num_frozen_str = ",".join(num_frozen_list)
                fps_str = ",".join(fps_list)

                print "F1-score: {}".format(1 - metric)
                print "{},{},{}\n".format(num_frozen_str, fps_str, cost)
        print "================================="


def main():
    args = get_args()
    app_datasets = [app_data.apps_by_name[app_name] for app_name in args.datasets]

    run_suffix = args.run_id + VERSION_SUFFIX

    for root, dirnames, filenames in os.walk(args.outdir):
        for filename in fnmatch.filter(filenames, '*'+run_suffix):
            os.remove(os.path.join(root, filename))

    # Generate app list
    for num_apps in range(2, args.num_apps_range+1):
      for budget in range(100, args.budget_range, 100):

        config_id = "example-n{}-b{}".format(num_apps, budget)
        config_suffix = config_id + VERSION_SUFFIX

        # Delete existing files with same suffix
        for root, dirnames, filenames in os.walk(args.outdir):
            for filename in fnmatch.filter(filenames, '*'+config_suffix):
                os.remove(os.path.join(root, filename))

        all_apps = []
        for i in range(0, num_apps):
            app_index = i % len(app_datasets)
            app = app_datasets[app_index].copy()
            app["app_id"] = i
            all_apps.append(app)

        run(args, all_apps, budget, config_suffix)


if __name__ == "__main__":
    main()
