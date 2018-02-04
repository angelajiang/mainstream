import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import pprint as pp
import random
import csv
import run_scheduler_simulator as sim


def main():
    """Find args in run_scheduler_simulator.py"""
    random.seed(1337)
    args = sim.get_args(simulator=False)
    all_apps = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    x_vote = args.x_vote
    min_metric = args.metric
    num_trials = args.trials

    versions = ["mainstream", "nosharing", "maxsharing"]

    for _ in range(num_trials):
        for version in args.versions:
            outfile = args.outfile_prefix
            if x_vote > 0:
                outfile += "-x" + str(x_vote)
                min_metric += "-x"
            outfile += "-" + versions[version]

            # Select app combinations.
            app_combs = sim.get_combs(args, all_apps, args.num_apps_range, outfile)
            if app_combs is None:
                continue
            # Run simulator and do logging.
            with open(outfile, "a+", 0) as f:
                writer = csv.writer(f)
                for entry_id, app_ids in app_combs:
                    apps = sim.apps_from_ids(app_ids, all_apps, x_vote)
                    s, stats = run_simulator(min_metric, apps, versions[version])
                    writer.writerow(sim.get_eval(entry_id, s, stats))
                    f.flush()


def run_simulator(min_metric, apps, version):
    s = Scheduler.Scheduler(min_metric, apps, app_data.video_desc,
                            app_data.model_desc, 0)

    fnr, fpr, cost, avg_rel_acc, num_frozen_list, target_fps_list = s.run(350, sharing=version)
    stats = {
        "fnr": fnr,
        "fps": fpr,
        "cost": cost,
        "avg_rel_acc": avg_rel_acc,
        "frozen": num_frozen_list,
        "fpses": target_fps_list,
    }
    return s, stats


if __name__ == "__main__":
    main()
