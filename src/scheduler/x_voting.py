import random

def bernoulli(p):
    return int(random.random() < p)

def is_x_detected(acc, conditional_probability, event_length, stride, x_vote, verbose = False):

    offset = int(stride * random.random()) # don't always sample first frame
    votes = 0
    detect = bernoulli(acc)
    for i in range(event_length):
        if (i + offset) % stride != 0:  # Bug: stride is a float, ill-defined
          continue
        if detect:
            votes += 1
            if votes >= x_vote:
                return True
            detect = bernoulli(conditional_probability)
        else:
            votes = 0
            detect = bernoulli(acc)
        previous_detected = detect
    return False

def calculate_miss_rate_montecarlo(acc=None,
                        event_length=None,
                        correlation=None,
                        stride=None,
                        x_vote=2,
                        trials=10000):
    conditional_probability = min(acc + correlation, 1)
    detections = [int(is_x_detected(acc, conditional_probability, int(event_length), stride, x_vote))
                    for _ in range(trials)]
    p_detected = sum(detections) / float(trials)
    p_detected_min = 0.00001
    p_detected = max(p_detected, p_detected_min)    # Probability should never be 0

    return 1 - p_detected
