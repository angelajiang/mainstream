import sys
import math


def get_apps_branched(schedule, branch_point):
    apps_branched = []
    apps_not_branched = []
    for app in schedule:
        if app[0] < branch_point: #double check
            apps_branched.append(app)
        else:
            apps_not_branched.append(app)
    return apps_branched, apps_not_branched

def get_relative_runtime(schedule, layer_latencies, num_layers):
    # Schedule = [(num_frozen, fps), ... ,(num_frozen, fps)]
    branch_points = list(set([a[0] for a in schedule]))
    branch_points.append(num_layers)
    seg_start = 0
    relative_runtime = 0
    for seg_end in branch_points:
        seg_latency = sum([layer_latencies[i] for i in range(seg_start, seg_end)]) #doublecheck

        apps_branched, apps_not_branched = get_apps_branched(schedule, seg_end)
        seg_fps = 0
        branched_fpses = [app[1] for app in apps_branched]
        not_branched_fpses = [app[1] for app in apps_not_branched]
        if len(apps_branched) > 0: #double check
            task_fps = sum(branched_fpses)
            seg_fps += task_fps
        if len(apps_not_branched) > 0: #double check
            base_fps = max(not_branched_fpses)
            seg_fps += base_fps

        relative_runtime += seg_latency * seg_fps
        seg_start = seg_end

    return relative_runtime

def get_false_neg_rate(p_identified, min_event_length_ms, max_fps, observed_fps):
    stride = max_fps / observed_fps
    d = min_event_length_ms / float(1000) * observed_fps
    if d < 1:
        #print "[WARNING] Event of length", min_event_length_ms, "ms cannot be detected at", max_fps, "FPS"
        return 1
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
    return p_miss

if __name__ == "__main__":

    min_event_length_ms = 500
    max_fps = 30

    p_identified1 = .7284
    observed_fps1 = 15

    p_identified2 = .882
    observed_fps2 = 2

    print 'Share everything:', get_false_neg_rate(p_identified1, min_event_length_ms, max_fps, observed_fps1)
    print 'Share nothing:', get_false_neg_rate(p_identified2, min_event_length_ms, max_fps, observed_fps2)
