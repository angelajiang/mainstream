import sys
import random
import math
from scipy.stats import linregress, hmean
import warnings

sys.path.append('src/scheduler')
import x_voting


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

def get_false_neg_rate(p_identified,
                       min_event_length_ms,
                       conditional_probability,
                       max_fps,
                       observed_fps,
                       x_vote = None):
    stride = max_fps / float(observed_fps)
    num_frames_in_event = float(min_event_length_ms) / 1000.0 * observed_fps

    if x_vote is None:
        false_neg_rate = calculate_miss_rate(p_identified, num_frames_in_event, conditional_probability, stride)
    else:
        false_neg_rate = x_voting.calculate_miss_rate(p_identified,
                                                      num_frames_in_event,
                                                      conditional_probability,
                                                      stride,
                                                      x_vote)

    return false_neg_rate

def get_false_pos_rate(p_identified,
                       p_identified_inv,
                       min_event_length_ms,
                       event_frequency,
                       cp_tp,
                       cp_fp,
                       max_fps,
                       observed_fps,
                       x_vote = None):
    """FPR = 1 - Precision"""
    # Assumes positive and negative have same event length
    stride = max_fps / float(observed_fps)
    num_frames_in_event = float(min_event_length_ms) / 1000.0 * observed_fps

    if x_vote is None:
        # Lower is better
        false_neg_rate = calculate_miss_rate(p_identified,
                                             num_frames_in_event,
                                             cp_tp,
                                             stride)

        # Higher is better
        false_neg_rate_inv  = calculate_miss_rate(p_identified_inv,
                                                  num_frames_in_event,
                                                  cp_fp,
                                                  stride)
    else:
        # Lower is better
        false_neg_rate = x_voting.calculate_miss_rate(p_identified,
                                                      num_frames_in_event,
                                                      cp_tp,
                                                      stride,
                                                      x_vote=x_vote)

        # Higher is better
        false_neg_rate_inv  = x_voting.calculate_miss_rate(p_identified_inv,
                                                           num_frames_in_event,
                                                           cp_fp,
                                                           stride,
                                                           x_vote=x_vote)


    # recall: Given an event, percent change we classify it as an event
    # negative_recall: Given an non-event, percent change we classify it as an event
    recall = 1 - false_neg_rate
    negative_recall = 1 - false_neg_rate_inv

    proportion_tp = event_frequency * recall
    proportion_fp = (1 - event_frequency) * negative_recall
    if proportion_tp + proportion_fp < 1e-10:
        precision = 0
        warnings.warn("No positive predictions, precision is ill-defined, setting to 0")
    else:
        precision = proportion_tp / float(proportion_tp + proportion_fp)

    return 1 - precision

def get_f1_score(p_identified,
                 p_identified_inv,
                 min_event_length_ms,
                 event_frequency,
                 cp_tp,
                 cp_fp,
                 max_fps,
                 observed_fps,
                 x_vote = None):

    # Assumes positive and negative have same event length
    fnr = get_false_neg_rate(p_identified,
                             min_event_length_ms,
                             cp_tp,
                             max_fps,
                             observed_fps,
                             x_vote)

    fpr = get_false_pos_rate(p_identified,
                             p_identified_inv,
                             min_event_length_ms,
                             event_frequency,
                             cp_tp,
                             cp_fp,
                             max_fps,
                             observed_fps,
                             x_vote)

    f1 = hmean([1 - float(fnr), 1 - float(fpr)])
    return f1

def calculate_miss_rate(p_identified, d, conditional_probability, stride):
# Calculate the probibility of misses as defined by what p_identinfied represents
# p_identified is the probability of a "hit"
# d: length of event to hit/miss in number of frames

    conditional_probability_miss = 1 - conditional_probability
    assert conditional_probability_miss < conditional_probability

    d = float(d)
    stride = float(stride)
    assert stride >= 1.

    # AJ: I don't think this is true. May have to think harder about what can be
    # floats and what can be ints
    #if d < 1:
    #    p_miss =  1.0
    #elif d < stride:

    if d < stride:
        p_encountered = d / stride
        p_hit = p_encountered * p_identified
        p_miss = 1 - p_hit
    else:
        r1 = math.ceil(d / stride)
        p1 = (d % stride) / stride
        r2 = math.floor(d / stride)
        p2 = 1 - p1
        p_not_identified = 1 - p_identified
        p_none_identified1 = math.pow(conditional_probability_miss, r1 - 1) * p_not_identified
        p_none_identified2 = math.pow(conditional_probability_miss, r2 - 1) * p_not_identified
        p_miss = p1 * p_none_identified1 + \
                 p2 * p_none_identified2

    return p_miss

