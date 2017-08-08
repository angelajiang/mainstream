import sys
sys.path.append('src/scheduler')
import static_scheduler
sys.path.append('data')
import app_data
import pprint as pp
import numpy as np
import time
import zmq

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    num_apps_range = int(sys.argv[1])
    outfile = sys.argv[2]
    thresholds = [0, 0.1, 0.05, 0.01, 0.005, 1]

    with open(outfile, "a+", 0) as f:
        for num_apps in range(1, num_apps_range + 1):
            for threshold in thresholds:

                # Get Schedule
                apps = []
                for i in range(1, num_apps + 1):
                    index = i % len(app_data.app_options)
                    app = app_data.app_options[index]
                    apps.append(app)
                    sched = static_scheduler.schedule(apps,
                                                      threshold,
                                                      app_data.model_desc)

                # Deploy schedule
                fpses = []
                for i in range(5):
                    socket.send_json(sched)
                    fps_message = socket.recv()
                    fpses.append(float(fps_message))
                avg_fps = np.average(fpses)
                stdev = np.std(fpses)
                line = str(num_apps) + "," + str(threshold) + "," + \
                       str(avg_fps) + "," + str(stdev) + "\n"
                f.write(line)
                print num_apps, threshold, avg_fps, stdev
