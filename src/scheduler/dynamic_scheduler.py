import sys
sys.path.append('src/scheduler')
import scheduler
import numpy as np
import zmq


def get_relative_accuracy(app, num_frozen):
    max_acc = max(app["accuracies"].values())
    cur_acc = app["accuracies"][num_frozen]
    rel_acc = (max_acc - cur_acc) / max_acc
    return rel_acc

def get_next_frozen_layer(app, num_frozen):
# Want more layers frozen
    for layers in sorted(app["accuracies"].keys()):
        if layers > num_frozen:
            return layers
    return num_frozen # Already at max

def schedule(apps, num_frozen_list, model_desc):
    return scheduler.schedule(apps, num_frozen_list, model_desc)

def get_num_frozen_list(apps, cur_num_frozen_list):
# Change at most one frozen layer to share more
# Returns num_frozen_list or None if we can't improve it
    num_frozen_list = []
    if cur_num_frozen_list == []:
        # First time around, so there is nothing to improve
        # Construct num_frozen_list that maximizes accuracy
        for app in apps:
            accs = app["accuracies"]
            max_acc = max(accs.values())
            best_num_frozen = \
                    max([k for k, v in accs.iteritems() if v == max_acc])
            print max_acc, best_num_frozen
            num_frozen_list.append(best_num_frozen)
    else:
        # Compare accuracy loss of changing num_frozen_layers for each app
        # Choose to change the one with least accuracy loss and highest
        # gain of frozen layers

        min_accuracy_loss = float("inf")
        target_app_index = None
        target_num_frozen = None
        target_num_frozen_inc = 0

        for index, app in enumerate(apps):
            cur_num_frozen = cur_num_frozen_list[index]

            rel_acc = get_relative_accuracy(app, cur_num_frozen)
            potential_num_frozen = get_next_frozen_layer(app, cur_num_frozen)

            if potential_num_frozen == cur_num_frozen:
                continue

            potential_rel_acc = \
                    get_relative_accuracy(app, potential_num_frozen)
            potential_loss = potential_rel_acc - rel_acc

            if potential_loss < min_accuracy_loss:
                min_accuracy_loss = potential_loss
                target_app_index = index
                target_num_frozen = potential_num_frozen
                target_num_frozen_inc = potential_num_frozen - cur_num_frozen

            elif potential_loss == min_accuracy_loss:
                # To break a tie, choose to freeze more layers
                potential_num_frozen_inc = potential_num_frozen - cur_num_frozen
                if potential_num_frozen_inc > target_num_frozen_inc:
                    target_app_index = index
                    target_num_frozen = potential_num_frozen
                    target_num_frozen_inc = potential_num_frozen_inc

        # Make improved num_frozen_list
        if min_accuracy_loss == float("inf"):
            return None
        else:
            num_frozen_list = cur_num_frozen_list
            num_frozen_list[target_app_index] = target_num_frozen

    return num_frozen_list

def run(apps, model_desc, min_fps):

    num_trials = 3
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    avg_fps = -1
    num_frozen_list = []
    iteration = 0

    # Iterate until we converge to min_fps
    print "Num apps:", len(apps), " Min FPS:", min_fps
    while (avg_fps < min_fps):

        # Get schedule
        num_frozen_list = get_num_frozen_list(apps, num_frozen_list)

        # There is no better schedule
        if num_frozen_list == None:
            return -1, -1, []

        sched = schedule(apps, num_frozen_list, model_desc)

        # Deploy schedule
        fpses = []
        for i in range(num_trials):
            socket.send_json(sched)
            fps_message = socket.recv()
            fpses.append(float(fps_message))
        avg_fps = np.average(fpses)
        stdev = np.std(fpses)
        print "i:", iteration, "fps:", avg_fps, "stdev:", stdev

        iteration += 1

    rel_accs = [get_relative_accuracy(app, num_frozen) \
                    for app, num_frozen in zip(apps, num_frozen_list)]

    return np.average(rel_accs), np.std(rel_accs), num_frozen_list
