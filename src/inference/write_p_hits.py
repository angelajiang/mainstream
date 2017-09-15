import random
import sys
import operator
sys.path.append('/users/ahjiang/src/mainstream/src/inference')
import inference_h5
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import math
#from collections import defaultdict


TRAIN_INDEX = 1 #Index of model output that corresponds to label "Train"

def get_dataset(base_dir):
    # Accepts dataset directory where each subdirectory is another instance
    d = defaultdict(list)
    for root, subdirs, files in os.walk(base_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            assert file_path.startswith(base_dir)
            suffix = file_path[len(base_dir):]
            suffix = suffix.lstrip("/")
            label = suffix.split("/")[0]
            d[label].append(file_path)
    return d

def get_dataset_size(dataset_dir):
    onlyfiles = [f for f in listdir(dataset_dir) if isfile(join(dataset_dir, f))]
    return len(onlyfiles)

def get_length_distribution(base_dir):
    # Returns list of number of files in each subdirectory of base_dir
    data_files = get_dataset(base_dir)
    sizes = [len(v) for k, v in data_files.iteritems()]
    return sizes

def get_accuracy(dataset_dirs, model_path):
    print "----------------------", model_path, "------------------------"
    for dataset_dir in dataset_dirs:
        predictions = inference_h5.predict(model_path, dataset_dir)
        identifications = sum([1 for p in predictions if p[TRAIN_INDEX] >= 0.5]) 
        p_identified = identifications / float(len(predictions))
        print dataset_dir, p_identified

def get_empirical_detection_probability_random(dataset_dirs, model_path, strides):
    # Calculate false negative rate in expectation empirically
    p_hits = {}
    num_trials = 10000
    for dataset_dir in dataset_dirs:
        print "--------------", dataset_dir, "---------------"
        predictions = inference_h5.predict(model_path, dataset_dir)
        event_length = float(len(predictions))
        for stride in strides:
            if event_length < stride:
                p_sampled = event_length / stride
                num_encounters = 1
            else:
                p_sampled = 1
                num_encounters = int(math.floor(event_length / stride))
            hits = 0
            for i in range(num_trials):
                hit = False
                choices = []
                for encounter in range(num_encounters):
                    choice = random.choice(range(len(predictions)))
                    prediction = predictions[choice]
                    if prediction[TRAIN_INDEX] > 0.5:
                        hit = True
                    choices.append(choice)
                if (hit):
                    hits += 1
            p_hit = p_sampled * (hits / float(num_trials))
            print "[Event 2], p_hit:", p_hit, ", num_encounters:", num_encounters
            if stride not in p_hits.keys():
                p_hits[stride] = []
            p_hits[stride].append(p_hit)
    return p_hits

def get_empirical_detection_probability_temporal(dataset_dirs, model_path, strides):
    # Calculate false negative rate in expectation empirically
    p_hits = {}
    num_trials = 10000
    for dataset_dir in dataset_dirs:
        print "--------------", dataset_dir, "---------------"
        predictions = inference_h5.predict(model_path, dataset_dir)
        event_length = float(len(predictions))
        for stride in strides:

            classifications = 0
            num_encounters = 0
            for i in range(num_trials):
                classified = False
                start_index = random.choice(range(stride))
                index = start_index
                while index < len(predictions):
                    prediction = predictions[index]
                    if prediction[TRAIN_INDEX] >= 0.5:
                        classified = True
                    index += stride
                    num_encounters += 1
                if (classified):
                    classifications += 1
            num_encounters_average = num_encounters / float(num_trials)
            ne = round(event_length / stride, 2)
            print "Num encounters:", num_encounters_average, "vs", ne

            p_hit = classifications / float(num_trials)
            print "[Event 2], strided:", stride, "p_hit:", p_hit
            if stride not in p_hits.keys():
                p_hits[stride] = []
            p_hits[stride].append(p_hit)
    return p_hits

def get_detection_probability(predictions, stride, event_length, is_independent):
    # Calculate false negative rate in expectation, assuming full independence
    # or full dependence

    identifications = sum([1 for p in predictions if p[TRAIN_INDEX] >= 0.5]) 
    p_identified = identifications / float(len(predictions))

    if event_length < stride:
        p_encountered = event_length / stride
        p_hit = p_encountered * p_identified
    else:
        if is_independent:
            mod = (event_length % stride)
            p1 = (event_length - (mod)) / event_length
            r1 = math.floor(event_length / stride)
            p2 = mod / event_length
            r2 = math.ceil(event_length / stride)
            p_not_identified = 1 - p_identified
            p_not_hit = p1 * math.pow(p_not_identified, r1) + \
                        p2 * math.pow(p_not_identified, r2)
            p_hit = 1 - p_not_hit
        else:
            p_hit = p_identified

    print "stride:", stride, "d:", event_length, "p_hit:", p_hit, "p_id:", p_identified
    return p_hit

def get_fnr_by_stride_and_slo(dataset_dirs, model_path, strides,
                              within_frames_slo, is_independent):
    p_hits = {}
    for dataset_dir in dataset_dirs:
        print "----------------", dataset_dir, "------------------"
        predictions = inference_h5.predict(model_path, dataset_dir)

        for stride in strides:
            for slo in within_frames_slo:
                d = float(min(slo, len(predictions)))
                p_hit = get_detection_probability(predictions, stride, d, is_independent)
                if stride not in p_hits.keys():
                    p_hits[stride] = {}
                if slo not in p_hits[stride].keys():
                    p_hits[stride][slo] = []
                p_hits[stride][slo].append(p_hit)
    return p_hits

def get_fnr_by_stride(dataset_dirs, model_path, strides, is_independent):
    p_hits = {}
    for dataset_dir in dataset_dirs:
        print "----------------", dataset_dir, "------------------"
        predictions = inference_h5.predict(model_path, dataset_dir)

        for stride in strides:
            d = float(len(predictions))
            p_hit = get_detection_probability(predictions, stride, d, is_independent)
            if stride not in p_hits.keys():
                p_hits[stride] = []
            p_hits[stride].append(p_hit)
    return p_hits

def runA(dataset_dirs, model_path, strides, within_frames_slo, output_file, is_independent):
# Get theoretical FNR by stride and slo
    p_hits = get_fnr_by_stride_and_slo(dataset_dirs,
                                       model_path,
                                       strides,
                                       within_frames_slo,
                                       is_independent)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(1))
    with open(output_file, "w+") as f:
        for stride, p_hits_by_slo in sorted_strides:
            sorted_slos = sorted(p_hits_by_slo.items(), key=operator.itemgetter(1))
            for slo, arr in sorted_slos:
                line = str(stride) + "," + str(slo) + "," + str(np.average(arr)) + "\n"
                f.write(line)

def runB(dataset_dirs, model_path, strides, output_file, is_independent):
# Get theoretical FNR by stride
    p_hits = get_fnr_by_stride(dataset_dirs,
                               model_path,
                               strides,
                               is_independent)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

def runC(dataset_dirs, model_path, strides, output_file):
# Get emprical FNR by stride, sample event randomly
    p_hits = get_empirical_detection_probability_random(dataset_dirs,
                                                 model_path,
                                                 strides)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

def runD(dataset_dirs, model_path, strides, output_file):
# Get emprical FNR by stride, sample event temporally
    p_hits = get_empirical_detection_probability_temporal(dataset_dirs,
                                                 model_path,
                                                 strides)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

if __name__ == "__main__":

    #AFN

    dataset_dirs = [
                    "/users/ahjiang/image-data/instances/train_images_resized/a/",
                    "/users/ahjiang/image-data/instances/train_images_resized/f/",
                    "/users/ahjiang/image-data/instances/train_images_resized/n/",
                    "/users/ahjiang/image-data/instances/train_images_resized/1/",
                    "/users/ahjiang/image-data/instances/train_images_resized/2/",
                    "/users/ahjiang/image-data/instances/train_images_resized/3/",
                    "/users/ahjiang/image-data/instances/train_images_resized/4/",
                    "/users/ahjiang/image-data/instances/train_images_resized/5/"
                    ]

    strides = range(1, 301, 1)
    #within_frames_slo = [1, 10, 20, 30, 40, 50]

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-313"

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-dependent"
    #runB(dataset_dirs, model_path, strides, output_file, True)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-independent"
    #runB(dataset_dirs, model_path, strides, output_file, False)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-random"
    runC(dataset_dirs, model_path, strides, output_file)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-temporal"
    runD(dataset_dirs, model_path, strides, output_file)
