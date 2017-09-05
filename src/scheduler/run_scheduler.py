import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data
import pprint as pp
import numpy as np
import time
import zmq

if __name__ == "__main__":

    num_apps_range = int(sys.argv[1])
    outfile = sys.argv[2]

    with open(outfile, "a+", 0) as f:
        for num_apps in range(1, num_apps_range+1):

            # Get Schedule
            apps = []
            for i in range(1, num_apps + 1):
                index = i % len(app_data.app_options)
                app = dict(app_data.app_options[index])
                app["app_id"] = i
                apps.append(app)

            s = Scheduler.Scheduler(apps, app_data.video_desc, app_data.model_desc)
            s.optimize_parameters(5000)

'''
            metric, avg_rel_acc, num_frozen_list, target_fps_list = s.run(50000)

            num_frozen_str = ",".join([str(x) for x in num_frozen_list])
            target_fps_str = ",".join([str(x) for x in target_fps_list])

            line = str(num_apps) + "," + str(round(metric, 4)) + "," + \
                   str(round(avg_rel_acc ,4)) + "," + \
                   num_frozen_str + "," + target_fps_str + "\n"
            f.write(line)
            '''
