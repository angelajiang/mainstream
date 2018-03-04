

import argparse
import csv
import scheduler_util
import Scheduler
import os
import app_data_mobilenets as app_data

import sys
sys.path.append('src/scheduler')
import run_scheduler_simulator as sim

VERSION_SUFFIX = ".v0"

# Directory structure
# outdir/
#   pointers.run_id.v0
#   setup/
#       configuration.config_id.v0
#       model.config_id.v0
#       environment.config_id.v0
#   schedules/
#       greedy.config_id.v0
#       exhaustive.config_id.v0

def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    #parser.add_argument("-n", "--num_apps", required=True, type=int)
    parser.add_argument("-b", "--budget", required=True, type=float)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names,
                                                       required=True,
                                                       help='provide at least one dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-r", "--run_id", required=True)
    parser.add_argument("-v", "--verbose", type=int, default=0)
    return parser.parse_args()


def write_cost_benefits_file(cost_benefits, outdir, filename):
    subdir = os.path.join(outdir, "setup");
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    outfile = os.path.join(subdir, "configuration." + filename)
    with open(outfile, "w+") as f:
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
    with open(outfile, "w+") as f:
        layer_costs_str = [str(c) for c in layer_costs]
        line = " ".join(layer_costs_str) + "\n"
        f.write(line)
    return outfile


def write_environment_file(budget, outdir, filename):
    subdir = os.path.join(outdir, "setup");
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    outfile = os.path.join(subdir, "environment." + filename)
    with open(outfile, "w+") as f:
        line = str(budget) + "\n"
        f.write(line)
    return outfile


def main():
    args = get_args()
    min_metric = args.metric
    app_datasets = [app_data.apps_by_name[app_name] for app_name in args.datasets]

    ####### TEMPORARY #######

    # Generate app list
    all_apps = []
    for i, app in enumerate(app_datasets):
        app["app_id"] = i
        all_apps.append(app)

    config_id = "example" + VERSION_SUFFIX

    ##########################

    s = Scheduler.Scheduler(min_metric, all_apps, app_data.video_desc,
                            app_data.model_desc, 0)

    # Get cost_benefits
    cost_benefits = s.get_cost_benefits()

    # Write cost benefits, model, and environment data for cpp fn
    f1 = write_cost_benefits_file(cost_benefits, args.outdir, config_id)
    f2 = write_model_file(s.model.layer_latencies, args.outdir, config_id)
    f3 = write_environment_file(args.budget, args.outdir, config_id)

    # Store filenames which point to schedule data
    # Each line represents one schedule-configuration
    pointers_file = os.path.join(args.outdir, "pointers." + args.run_id + VERSION_SUFFIX)
    with open(pointers_file, "w+") as f:
        line = "{}\n".format(config_id)
        f.write(line)
        f.flush()

    # Write output with mainstream-simulator schedules
    s, stats = sim.run_simulator("f1", all_apps, args.budget)

    subdir = os.path.join(args.outdir, "schedules");
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    outfile = os.path.join(subdir, "greedy." + config_id)

    with open(outfile, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(sim.get_eval(len(all_apps), s, stats))
        f.flush()

    if (bool(args.verbose)):
        min_metric = 2
        print "[Warning] Trying to get all combos in python"
        schedules, metrics, costs = s.get_parameter_options();
        for schedule, metric, cost in zip(schedules, metrics, costs):
            if cost <= args.budget and metric < min_metric:
                app0 = schedule[0]
                app1 = schedule[1]
                fps0 = app0.target_fps
                fps1 = app1.target_fps
                nf0  = app0.num_frozen
                nf1 = app1.num_frozen

                print "F1-score: {}".format(1 - metric)
                print "{},{},{},{},{}\n".format(nf0, nf1, fps0, fps1, cost)


if __name__ == "__main__":
    main()
