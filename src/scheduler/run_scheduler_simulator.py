import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import pprint as pp
import numpy as np
import time
import zmq

if __name__ == "__main__":

    num_apps_range = int(sys.argv[1])
    outfile_prefix = sys.argv[2]

    outfile = outfile_prefix + "-mainstream-simulator"

    min_metric = "f1"

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
