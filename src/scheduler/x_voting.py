import random

def bernoulli(p):
    return int(random.random() < p)

def is_x_detected(acc, correlation, event_length, stride, x_vote):
    offset = int(stride * random.random()) # don't always sample first frame
    votes = 0
    previous_detected = None
    for i in range(event_length):
        if (i + offset) % stride is not 0:
            continue
        if previous_detected:
            detect = bernoulli(correlation)
        else:
            detect = bernoulli(acc)
        if detect:
            votes += 1
            if votes is x_vote:
                return True
        else:
            votes = 0
        previous_detected = detect
    return False

def calculate_miss_rate(acc=None,
                        event_length=None,
                        correlation=None,
                        stride=None,
                        x_vote=2,
                        trials=10000):
    detections = [int(is_x_detected(acc, correlation, int(event_length), stride, x_vote))
                    for _ in range(trials)]
    p_detected = sum(detections) / float(trials)
    return 1 - p_detected
