import sys
sys.path.append('src/scheduler')
import dynamic_scheduler
sys.path.append('data')
import app_data
import pprint as pp
import numpy as np
import time
import zmq

if __name__ == "__main__":

    num_apps_range = int(sys.argv[1])
    thresholds_range = int(sys.argv[2])
    outfile = sys.argv[3]

    with open(outfile, "a+", 0) as f:
        for num_apps in range(1, num_apps_range + 1):
            for threshold in range(1, thresholds_range + 1):
                # Get Schedule
                apps = []
                for i in range(1, num_apps + 1):
                    index = i % len(app_data.app_options)
                    app = app_data.app_options[index]
                    apps.append(app)

                avg_rel_acc, stdev_rel_acc, num_frozen_list= \
                        dynamic_scheduler.run(apps,
                                              app_data.model_desc,
                                              threshold)
                num_frozen_str = ",".join([str(x) for x in num_frozen_list])
                line = str(num_apps) + "," + str(threshold) + "," + \
                       str(avg_rel_acc) + "," + str(stdev_rel_acc) + \
                       "," + num_frozen_str + "\n"
                f.write(line)
