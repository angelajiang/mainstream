import sys
import math


def get_false_neg_rate(p_identified, min_event_length_ms, max_fps, observed_fps):
    stride = max_fps / observed_fps
    d = min_event_length_ms / float(1000) * observed_fps
    if d < 1:
        print "[WARNING] Event of length", min_event_length_ms, "ms cannot be detected at", max_fps, "FPS"
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
