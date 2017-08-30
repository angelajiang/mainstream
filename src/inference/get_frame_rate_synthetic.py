import sys
import operator
sys.path.append('src/inference')
import inference_h5
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import math
#from collections import defaultdict

accuracy_flowers_inception = {#0:0.882,
                              #4:0.882,
                              7:0.8834,
                              10:0.882,
                              #11:0.8807,
                              14:0.8834,
                              #17:0.8807,
                              18:0.882,
                              41:0.8807,
                              64:0.8807,
                              87:0.8807,
                              #101:0.8765,
                              133:0.8779,
                              165:0.8765,
                              197:0.8697,
                              #229:0.8615,
                              249:0.8669,
                              280:0.8477,
                              311:0.7284}


def get_detection_probability(num_frozen, strides, within_frames_slo):
    p_hits = {}

    for stride in strides:
        for slo in within_frames_slo:

            p_identified = accuracy_flowers_inception[num_frozen]
            d = float(slo)
            if d < stride:
                p_encountered = d / stride
                p_hit = p_encountered * p_identified
            else:
                mod = (d % stride)
                p1 = (d - (mod)) / d
                r1 = math.floor(d / stride)
                p2 = mod / d
                r2 = math.ceil(d / stride)
                p_not_identified = 1 - p_identified
                p_not_hit = p1 * math.pow(p_not_identified, r1) + \
                            p2 * math.pow(p_not_identified, r2)
                p_hit = 1 - p_not_hit

            print "stride:", stride, "slo:", slo, "p_hit:", p_hit, "p_id:", p_identified

            if stride not in p_hits.keys():
                p_hits[stride] = {}
            if slo not in p_hits[stride].keys():
                p_hits[stride][slo] = []
            p_hits[stride][slo].append(p_hit)

    return p_hits

def run(num_frozen, strides, within_frames_slo, output_file):
    p_hits = get_detection_probability(num_frozen,
                                       strides,
                                       within_frames_slo)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(1))
    with open(output_file, "w+") as f:
        for stride, p_hits_by_slo in sorted_strides:
            sorted_slos = sorted(p_hits_by_slo.items(), key=operator.itemgetter(1))
            for slo, arr in sorted_slos:
                line = str(stride) + "," + str(slo) + "," + str(np.average(arr)) + "\n"
                f.write(line)

if __name__ == "__main__":

    strides = range(10, 610, 10)
    within_frames_slo = [1, 10, 20, 30, 40, 50]
    num_frozen_list = accuracy_flowers_inception.keys()

    for num_frozen in num_frozen_list:
        output_file = "/users/ahjiang/src/mainstream/log/frame-rate/flowers/synthetic/" + str(num_frozen)
        run(num_frozen, strides, within_frames_slo, output_file)

