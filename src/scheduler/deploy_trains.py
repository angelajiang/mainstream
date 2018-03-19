import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import train_app_data as app_data
import pprint as pp
import numpy as np
import time
import zmq

if __name__ == "__main__":

    num_apps = int(sys.argv[1])
    version = int(sys.argv[2])
    outfile_prefix = sys.argv[3]

    if version not in range(0, 3):
        print "Version should be 0 for mainstream, 1 for nosharing, 2 for maxsharing"
        sys.exit()

    outfile_nosharing = outfile_prefix + "-nosharing"
    outfile_maxsharing = outfile_prefix + "-maxsharing"
    outfile_mainstream = outfile_prefix + "-mainstream"

    params_nosharing = [True, False]
    params_maxsharing = [False, True]
    params_mainstream = [False, False]

    outfiles = [outfile_mainstream, outfile_nosharing, outfile_maxsharing]
    params_options = [params_mainstream, params_nosharing, params_maxsharing]

    outfile = outfiles[version]
    params = params_options[version]

    with open(outfile, "a+", 0) as f:

        # Get Schedule
        apps = []
        app = dict(app_data.app_options[0]) # Add train
        app["app_id"] = 1
        apps.append(app)
        for i in range(2, num_apps + 1):
            # Add others
            index = i % len(app_data.app_options)
            app = dict(app_data.app_options[1])
            app["app_id"] = i
            apps.append(app)

        s = Scheduler.Scheduler(apps, app_data.video_desc,
                                app_data.model_desc, 0)

        metric, cost, avg_rel_acc, num_frozen_list, target_fps_list = s.run(154,
                                                                      params[0],
                                                                      params[1])
        print "Observed FNR:", metric, ", Frozen:", num_frozen_list, \
                ", FPS:",  target_fps_list, ", Cost:", cost

        num_frozen_str = ",".join([str(x) for x in num_frozen_list])
        target_fps_str = ",".join([str(x) for x in target_fps_list])

        line = str(num_apps) + "," + str(round(metric, 4)) + "," + \
               str(round(avg_rel_acc ,4)) + "," + \
               num_frozen_str + "," + target_fps_str + "," + str(cost) + "\n"
        f.write(line)
