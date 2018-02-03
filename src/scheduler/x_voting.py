from collections import deque
import math
import random
import warnings


def miss_rate_with_x_vote(acc, conditional_probability, hops, x_vote):
    if hops < x_vote:
        warnings.warn('Not enough bites (hops < x_vote): {} < {}'.format(hops, x_vote))
    q = deque([['', 1., acc, 0]])
    probs = [0., 0.] # [miss, hit]
    while q:
        c, c_prob, multiplier, cnt_running = q.popleft()
        if cnt_running == x_vote:
            probs[1] += c_prob
            continue
        elif len(c) >= hops:
            probs[0] += c_prob
            continue
        elif cnt_running > x_vote:
            raise
        q.append([c + 'T', c_prob * multiplier, conditional_probability, cnt_running + 1])
        q.append([c + 'F', c_prob * (1. - multiplier), acc, 0])
    assert abs(sum(probs) - 1.) < .0001
    return probs

        
def get_hops_prob_dist(event_length, stride):
    event_length = float(event_length)
    r1 = int(math.floor(event_length / stride))
    result = {r1: (stride - (event_length % stride)) / stride}
    r2 = int(math.ceil(event_length / stride))
    if r1 != r2:
        result[r2] = (event_length % stride) / stride
    assert abs(sum(result.values()) - 1.) < .0001
    return result


def calculate_miss_rate(acc=None,
                        event_length=None,
                        correlation=None,
                        stride=None,
                        x_vote=2):
    assert stride >= 1., stride
    conditional_probability_hit = correlation
    # assert conditional_probability_hit >= acc, "{} < {}".format(conditional_probability_hit, acc)
    if conditional_probability_hit < acc:
        warnings.warn("{} < {}, setting cond_prob_hit = acc".format(conditional_probability_hit, acc), stacklevel=2)
        conditional_probability_hit = acc
    hops_prob_dist = get_hops_prob_dist(event_length, stride)
    result = [0., 0.]
    for hops, weight in hops_prob_dist.items():
        dist = miss_rate_with_x_vote(acc, conditional_probability_hit, hops, x_vote)
        result[0] += weight * dist[0]
        result[1] += weight * dist[1]
    assert abs(sum(result) - 1.) < 1e-5
    return result[0]

# def bernoulli(p):
#     return int(random.random() < p)

# def is_x_detected(acc, conditional_probability, event_length, stride, x_vote, verbose = False):

#     offset = int(stride * random.random()) # don't always sample first frame
#     votes = 0
#     detect = bernoulli(acc)
#     for i in range(event_length):
#         if (i + offset) % stride != 0:  # Bug: stride is a float, ill-defined
#           continue
#         if detect:
#             votes += 1
#             if votes >= x_vote:
#                 return True
#             detect = bernoulli(conditional_probability)
#         else:
#             votes = 0
#             detect = bernoulli(acc)
#         previous_detected = detect
#     return False

# def calculate_miss_rate_montecarlo(acc=None,
#                         event_length=None,
#                         correlation=None,
#                         stride=None,
#                         x_vote=2,
#                         trials=10000):
#     conditional_probability = min(acc + correlation, 1)
#     detections = [int(is_x_detected(acc, conditional_probability, int(event_length), stride, x_vote))
#                     for _ in range(trials)]
#     p_detected = sum(detections) / float(trials)
#     p_detected_min = 0.00001
#     p_detected = max(p_detected, p_detected_min)    # Probability should never be 0

#     return 1 - p_detected
