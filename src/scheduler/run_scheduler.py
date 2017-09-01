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

    outfile = sys.argv[1]

    with open(outfile, "a+", 0) as f:
        num_apps = 2

        # Get Schedule
        apps = []
        for i in range(1, num_apps + 1):
            index = i % len(app_data.app_options)
            app = app_data.app_options[index]
            apps.append(app)

        s = Scheduler.Scheduler(apps, app_data.video_desc, app_data.model_desc)
        s.run(5000)

        '''
        avg_rel_acc, num_frozen_list = s.run()

        num_frozen_str = ",".join([str(x) for x in num_frozen_list])

        line = str(num_apps) + "," + str(round(avg_rel_acc,4)) + "," + \
               num_frozen_str + "\n"
        f.write(line)
        '''
