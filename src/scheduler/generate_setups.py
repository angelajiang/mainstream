

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

def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    parser.add_argument("-n", "--num_apps_range", required=True, type=int)
    parser.add_argument("-c", "--config_file", required=True)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-s", "--num_setups", required=True, type=int)
    parser.add_argument("-r", "--run_id", required=True)
    parser.add_argument("-f", "--stream_fps", required=True, type=int)
    return parser.parse_args()

def main():
    args = get_args()

    setup_generator = Setup.SetupGenerator()
    setup_generator.parse_config(args.config_file)
    print "Total possible params:", setup_generator.num_param_setups

    setups_file = os.path.join(args.outdir, "setups." + args.run_id)
    if os.path.exists(setups_file):
        print "Loading setups from file."
    else:
        print "Generating setups."

        all_setups = []
        for num_apps in range(2, args.num_apps_range+1):
          setups = setup_generator.generate_setups(args.num_setups, num_apps, args.stream_fps)
          all_setups += setups

        setup_generator.serialize_setups(all_setups, setups_file)

    all_setups = setup_generator.deserialize_setups(setups_file + ".pickle")

if __name__ == "__main__":
    main()
