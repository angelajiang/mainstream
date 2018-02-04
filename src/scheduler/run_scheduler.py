import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data_mobilenets as app_data
import pprint as pp
import time
import zmq

if __name__ == "__main__":

    num_apps_range = int(sys.argv[1])
    version = int(sys.argv[2])
    outfile_prefix = sys.argv[3]

    if version not in range(0, 3):
        print "Version should be 0 for mainstream, 1 for nosharing, 2 for maxsharing"
        sys.exit()

    outfile_mainstream = outfile_prefix + "-mainstream"
    outfile_nosharing = outfile_prefix + "-nosharing"
    outfile_maxsharing = outfile_prefix + "-maxsharing"

    params_mainstream = [False, False]
    params_nosharing = [True, False]
    params_maxsharing = [False, True]

    outfiles = [outfile_mainstream, outfile_nosharing, outfile_maxsharing]
    params_options = [params_mainstream, params_nosharing, params_maxsharing]

    outfile = outfiles[version]
    params = params_options[version]

    outfiles = [outfile_maxsharing, outfile_nosharing]
    params_options = [params_maxsharing, params_nosharing]

    num_trials = 1

    metric = "f1"

    for i in range(num_trials):
        for outfile, params in zip(outfiles, params_options):
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

                    s = Scheduler.Scheduler(metric, apps, app_data.video_desc,
                                            app_data.model_desc, 0)

                    fnr, fpr, cost, avg_rel_acc, num_frozen_list, target_fps_list = s.run(350,
                                                                                    params[0],
                                                                                    params[1])

                    print "(Observed FNR: {fnr}, FPR: {fpr} \n \
                            Frozen: {frozen}, FPR: {fps}, Cost: {cost}) ".format(**{
                                    "fnr": fnr,
                                    "fpr": fpr,
                                    "cost": cost,
                                    "fps": target_fps_list,
                                    "frozen": num_frozen_list})

                    num_frozen_str = ",".join([str(x) for x in num_frozen_list])
                    target_fps_str = ",".join([str(x) for x in target_fps_list])

                    line = str(num_apps) + "," + str(fnr) + "," + str(fpr) + "," + \
                           str(round(avg_rel_acc ,4)) + "," + \
                           num_frozen_str + "," + target_fps_str + "\n"
                    f.write(line)
