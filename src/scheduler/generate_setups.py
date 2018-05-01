

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
import Setup

# Directory structure
# outdir/
#   pointers.run_id.v0
#   setups.run_id.v0
#   setups.run_id.v0.pickle
#   setup/
#       configuration.setup_suffix.v0
#       model.setup_suffix.v0
#       environment.setup_suffix.v0
#   schedules/
#       greedy.run_id.v0
#       exhaustive.run_id.v0


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-n", "--num_apps", required=True, type=int)
    parser.add_argument("-sn", "--sweep_num_apps", type=int, default=1, choices=[0, 1])
    parser.add_argument("-c", "--config_file", required=True)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-m", "--metric", default="f1")
    parser.add_argument("-s", "--num_setups", required=True, type=int)
    parser.add_argument("-r", "--run_id", required=True)
    parser.add_argument("-f", "--stream_fps", required=True, type=int)
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


def write_intermediate_files(args, setup, setup_suffix):
    print "Writing intermediate I/O file."

    apps = [app.to_map() for app in setup.apps]

    s = Scheduler.Scheduler(args.metric,
                            apps,
                            setup.video_desc.to_map(),
                            app_data.model_desc,
                            0)

    # Write cost benefits, model, and environment data for cpp fn
    cost_benefits = s.get_cost_benefits()
    f1 = write_cost_benefits_file(cost_benefits, args.outdir, setup_suffix)
    f2 = write_model_file(s.model.layer_latencies, args.outdir, setup_suffix)

    return


def main():
    args = get_args()

    setup_generator = Setup.SetupGenerator()
    setup_generator.parse_config(args.config_file)
    print "Number of params configurations (not including apps):", setup_generator.num_param_setups

    setups_file = os.path.join(args.outdir, "setups." + args.run_id)
    if os.path.exists(setups_file):
        print "Loading setups from file."
    else:
        print "Generating setups."

        all_setups = []
        if args.sweep_num_apps == 1:
            for num_apps in range(2, args.num_apps + 1):
              setups = setup_generator.generate_setups(args.num_setups, num_apps, args.stream_fps)
              all_setups += setups
        elif args.sweep_num_apps == 0:
            setups = setup_generator.generate_setups(args.num_setups, args.num_apps, args.stream_fps)
            all_setups = setups
        else:
            sys.exit()

        setup_generator.serialize_setups(all_setups, setups_file)

    all_setups = setup_generator.deserialize_setups(setups_file + ".pickle")

    pointers_file = os.path.join(args.outdir, "pointers." + args.run_id)
    pointers_f = open(pointers_file, "w+")

    for setup in all_setups:
      # Write out filenames which point to schedule data
      setup_suffix = setup.uuid
      line = "{}\n".format(setup.serialized())
      pointers_f.write(line)
      pointers_f.flush()

      write_intermediate_files(args, setup, setup_suffix)

if __name__ == "__main__":
    main()
