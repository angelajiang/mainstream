import sys
import random
import numpy as np
import math


def get_apps_branched(schedule, branch_point):
    apps_branched = []
    apps_not_branched = []
    for unit in schedule:
        if unit.num_frozen < branch_point: #double check
            apps_branched.append(unit)
        else:
            apps_not_branched.append(unit)
    return apps_branched, apps_not_branched

def get_cost(num_frozen, target_fps, layer_latencies):
    ### Cost of task-specific layers. Doesn't take trunk into account
    num_total_layers = len(layer_latencies)
    seg_latency = \
        sum([layer_latencies[i] for i in range(num_frozen, num_total_layers)])
    cost = seg_latency * target_fps
    return cost

def get_cost_schedule(schedule, layer_latencies, num_layers):
    ### Cost of full schedule
    ### Measure based on sum of inference/sec of each layer
    # Schedule = [ScheduleUnit...]
    branch_points = list(set([unit.num_frozen for unit in schedule]))
    branch_points.append(num_layers)
    seg_start = 0
    cost = 0
    for seg_end in branch_points:
        seg_latency = sum([layer_latencies[i] for i in range(seg_start, seg_end)]) #doublecheck

        apps_branched, apps_not_branched = get_apps_branched(schedule, seg_end)
        seg_fps = 0
        branched_fpses = [unit.target_fps for unit in apps_branched]
        not_branched_fpses = [unit.target_fps for unit in apps_not_branched]
        if len(apps_branched) > 0: #double check
            task_fps = sum(branched_fpses)
            seg_fps += task_fps
        if len(apps_not_branched) > 0: #double check
            base_fps = max(not_branched_fpses)
            seg_fps += base_fps

        cost += seg_latency * seg_fps
        seg_start = seg_end

    return cost

def get_acc_dist(accuracy, sigma):
    # Make a distribution of accuracies, centered around accuracy value
    # Represents different accuracies for difference instances of events.
    # E.g. a train classifier has 70% accuracy. But for trains at night,
    # it's 60% accurate, and in the daytime 80% accurate
    num_events = 10000
    acc_dist = [random.gauss(accuracy, sigma) for i in range(num_events)]
    return acc_dist

def get_false_neg_rate_with_dependence(p_identified_list, min_event_length_ms, max_fps, observed_fps):
    stride = max_fps / float(observed_fps)
    d = min_event_length_ms / 1000. * observed_fps
    p_misses = []
    # TOOD: Could be vectorized.
    for p_identified  in p_identified_list:
        if d < 1:
            #print "[WARNING] Event of length", min_event_length_ms, "ms cannot be detected at", max_fps, "FPS"
            p_miss = 1.
        else:
            if d < stride:
                p_encountered = d / stride
                p_hit = p_encountered * p_identified
            else:
                p_hit = p_identified
            p_miss = 1. - p_hit
        p_misses.append(p_miss)

    return sum(p_misses) / len(p_misses)

def get_false_neg_rate(p_identified_list, min_event_length_ms, max_fps, observed_fps, dependent = False):
    stride = max_fps / float(observed_fps)
    d = min_event_length_ms / float(1000) * observed_fps
    p_misses = []
    for p_identified  in p_identified_list:
        if d < 1:
            #print "[WARNING] Event of length", min_event_length_ms, "ms cannot be detected at", max_fps, "FPS"
            p_miss =  1.0
        if d < stride:
            p_encountered = d / stride
            p_hit = p_encountered * p_identified
            p_miss = 1 - p_hit
        else:
            mod = (d % stride)
            p1 = (d - (mod)) / d
            r1 = math.floor(d / stride)
            p2 = mod / d
            r2 = math.ceil(d / stride)
            p_not_identified = 1 - p_identified
            p_miss = p1 * math.pow(p_not_identified, r1) + \
                        p2 * math.pow(p_not_identified, r2)
        p_misses.append(float(p_miss))

    return sum(p_misses) / len(p_misses)

if __name__ == "__main__":

    min_event_length_ms = 500
    max_fps = 30

    p_identified1 = .7284
    observed_fps1 = 15

    p_identified2 = .882
    observed_fps2 = 2

    print 'Share everything:', get_false_neg_rate(p_identified1, min_event_length_ms, max_fps, observed_fps1)
    print 'Share nothing:', get_false_neg_rate(p_identified2, min_event_length_ms, max_fps, observed_fps2)
