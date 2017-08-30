import sys
sys.path.append('src/scheduler')
import scheduler
import numpy as np
import zmq


def run(apps, model_desc, min_fps):

    num_trials = 1
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    # Iterate until we converge to min_fps
    print "Num apps:", len(apps), " Min FPS:", min_fps
    sched = scheduler.make_streamer_schedule_no_sharing(apps, model_desc)

    num_frozen_list = []

    # Deploy schedule
    fpses = []
    for i in range(num_trials):
        socket.send_json(sched)
        fps_message = socket.recv()
        fpses.append(float(fps_message))
    avg_fps = np.average(fpses)
    stdev = np.std(fpses)

    #rel_accs = [get_relative_accuracy(app, num_frozen) \
    #                for app, num_frozen in zip(apps, num_frozen_list)]
    rel_accs = [1 for app in apps]

    return np.average(rel_accs), num_frozen_list
