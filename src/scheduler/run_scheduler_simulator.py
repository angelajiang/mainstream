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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("num_apps_range", type=int)
    parser.add_argument("x_vote", type=int, default=0)
    parser.add_argument("outfile_prefix")
    parser.add_argument("-m", "--metric", default="f1")
    args = parser.parse_args()
    num_apps_range = args.num_apps_range
    x_vote = args.x_vote
    outfile_prefix = args.outfile_prefix
    min_metric = args.metric

    if x_vote > 0:
        outfile = outfile_prefix + "-x" + str(x_vote) + "-mainstream-simulator"
        min_metric += "-x"

    else:
        outfile = outfile_prefix + "-mainstream-simulator"

    with open(outfile, "a+", 0) as f:
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

            metric = s.optimize_parameters(350)
            rel_accs = s.get_relative_accuracies()
            avg_rel_acc = np.average(rel_accs)

            # Get streamer schedule
            sched = s.make_streamer_schedule()

            # Use target_fps_str in simulator to avoid running on the hardware
            fnr, fpr, cost = s.get_observed_performance(sched, s.target_fps_list)

            print "Metric:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
            print "FNR:", fnr, ", FPR:", fpr

            num_frozen_str = ",".join([str(x) for x in s.num_frozen_list])
            target_fps_str = ",".join([str(x) for x in s.target_fps_list])

            line = str(num_apps) + "," + str(fnr) + "," + str(fpr) + "," + \
                   str(round(avg_rel_acc ,4)) + "," + \
                   num_frozen_str + "," + target_fps_str + "\n"
            f.write(line)
