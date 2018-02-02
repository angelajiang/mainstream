import sys
import operator
sys.path.append('/users/ahjiang/src/mainstream/src/inference')
import inference_h5
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import math
import itertools    
from collections import defaultdict


TRAIN_INDEX = 0

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

def get_conditional_probability(dataset_dirs, model, index):
    num_same = 0
    num_total = 0
    for dataset_dir in dataset_dirs:
        predictions = model.predict(dataset_dir)
        if predictions == []:
            continue
        binary_predictions = [1 if p[index] >= 0.5 else 0 for p in predictions]
        combos = list(itertools.combinations(binary_predictions, 2))
        for c in combos:
            if c[0] == 0:
                num_total += 1
                if c[1] == 0:
                    num_same += 1

    if num_total == 0:
        return -1

    cp = float(num_same) / num_total
    return cp

def get_accuracy(dataset_dirs, model, index):
    accs = []
    num_frames = []
    for dataset_dir in dataset_dirs:
        predictions = model.predict(dataset_dir)
        if predictions == []:
            continue
        identifications = sum([1 for p in predictions if p[index] >= 0.5]) 
        p_identified = identifications / float(len(predictions))
        accs.append(p_identified)
        num_frames.append(len(predictions))
        print dataset_dir, p_identified
    total_frames = sum(num_frames)
    freqs = [n / float(total_frames) for n in num_frames]
    acc = sum([a * f for a, f in zip(accs, freqs)])
    return acc

def get_empirical_detection_probability_random(dataset_dirs, model, strides):
    # Calculate false negative rate in expectation empirically
    p_hits = {}
    for dataset_dir in dataset_dirs:
        print "----------------------", dataset_dir, "------------------------"
        predictions = model.predict(dataset_dir)
        print predictions
        if predictions == []:
            continue

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

def get_detection_probability(stride, predictions, model_acc, event_length, is_independent, correlation):
    # Calculate false negative rate in expectation, assuming full independence
    # or full dependence or a provided correlation. First check if correlation
    # is provided. If it's none, use is_independent variable to assume full or
    # no independence


    if correlation != None or not is_independent:
        identifications = sum([1 for p in predictions if p[index] >= 0.5]) 
        p_identified = identifications / float(len(predictions))
    else:
        p_identified = model_acc

    if event_length < stride:
        p_encountered = event_length / stride
        p_hit = p_encountered * p_identified
    else:
        mod = (event_length % stride)
        p1 = (event_length - (mod)) / event_length
        r1 = math.floor(event_length / stride)
        p2 = mod / event_length
        r2 = math.ceil(event_length / stride)
        p_not_identified = 1 - p_identified

        if correlation != None:
            conditional_probability = correlation
        elif is_independent:
            conditional_probability = p_not_identified
        else:
            conditional_probability = 1

        p_none_identified1 = math.pow(conditional_probability, r1 - 1) * p_not_identified
        p_none_identified2 = math.pow(conditional_probability, r2 - 1) * p_not_identified
        p_not_hit = p1 * p_none_identified1 + \
                    p2 * p_none_identified2
        p_hit = 1 - p_not_hit

    print "stride:", stride, "d:", event_length, "p_hit:", p_hit, "p_id:", p_identified
    return p_hit

def get_fnr_by_stride_and_slo(dataset_dirs, model, strides,
                              within_frames_slo, is_independent,
                              correlation):
    p_hits = {}
    for dataset_dir in dataset_dirs:
        print "----------------", dataset_dir, "------------------"
        predictions = model.predict(dataset_dir)
        print predictions
        if predictions == []:
            continue

        identifications = sum([1 for p in predictions if p[1] >= 0.5]) 
        p_identified = identifications / float(len(predictions))

        for stride in strides:
            for slo in within_frames_slo:

                d = float(min(slo, len(predictions)))
                p_hit = get_detection_probability(stride,
                                                  predictions,
                                                  p_identified,
                                                  d,
                                                  is_independent,
                                                  correlation)
                if stride not in p_hits.keys():
                    p_hits[stride] = {}
                if slo not in p_hits[stride].keys():
                    p_hits[stride][slo] = []
                p_hits[stride][slo].append(p_hit)

    return p_hits

def get_fnr_by_stride(dataset_dirs, model, strides, model_acc, is_independent, correlation):
    p_hits = {}
    for dataset_dir in dataset_dirs:
        predictions = model.predict(dataset_dir)
        if predictions == []:
            continue
        identifications = sum([1 for p in predictions if p[1] >= 0.5]) 
        p_identified = identifications / float(len(predictions))
        print dataset_dir, p_identified

        for stride in strides:
            d = float(get_dataset_size(dataset_dir))
            p_hit = get_detection_probability(stride, predictions, model_acc, d, is_independent, correlation)
            if stride not in p_hits.keys():
                p_hits[stride] = []
            p_hits[stride].append(p_hit)
    return p_hits

def runA(dataset_dirs, model, strides, acc, within_frames_slo, output_file, is_independent):
# Get theoretical FNR by stride and slo
    p_hits = get_fnr_by_stride_and_slo(dataset_dirs,
                                       model,
                                       strides,
                                       acc,
                                       within_frames_slo,
                                       is_independent)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(1))
    with open(output_file, "w+") as f:
        for stride, p_hits_by_slo in sorted_strides:
            sorted_slos = sorted(p_hits_by_slo.items(), key=operator.itemgetter(1))
            for slo, arr in sorted_slos:
                line = str(stride) + "," + str(slo) + "," + str(np.average(arr)) + "\n"
                f.write(line)

def runB(dataset_dirs, model, strides, acc, output_file, is_independent, correlation = None):
# Get theoretical FNR by stride
    p_hits = get_fnr_by_stride(dataset_dirs,
                               model,
                               strides,
                               acc,
                               is_independent,
                               correlation)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

def runC(dataset_dirs, model, strides, output_file):
# Get emprical FNR by stride, sample event randomly
    p_hits = get_empirical_detection_probability_random(dataset_dirs,
                                                 model,
                                                 strides)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

def runD(dataset_dirs, model, strides, output_file):
# Get emprical FNR by stride, sample event temporally
    p_hits = get_empirical_detection_probability_temporal(dataset_dirs,
                                                 model,
                                                 strides)

    sorted_strides = sorted(p_hits.items(), key=operator.itemgetter(0))
    with open(output_file, "w+") as f:
        for stride, p_hits in sorted_strides:
            line = str(stride) + "," + str(np.average(p_hits)) + "\n"
            f.write(line)

if __name__ == "__main__":

    location = "/datasets/BigLearning/ahjiang/"
    location = "../mainstream/"
    dataset_dirs = ["{}image-data/instances/atrium/pedestrian/{}/".format(location, i) for i in range(53)]
    #AFN
    dataset_dirs = ["{}image-data/instances/train_images_resized/pedestrian/{}/".format(location, i) for i in ['a', 'f', 'n', 1, 2, 3, 4, 5]]


    for d in dataset_dirs:
        size = get_dataset_size(d)
        print d, size

    strides = range(1, 301, 1)
    #within_frames_slo = [1, 10, 20, 30, 40, 50]

    # nn = "mobilenets-9"
    nn = "mobilenets-84"
    # nn = "inception-313"
    model_name = "atrium-" + nn
    model_path = "../models/atc/pedestrian/atrium/" + model_name
    # model = "/datasets/BigLearning/ahjiang/models/trains-new/trains-no-afn-313"

    model = inference_h5.Model(model_path)
    model.gen_predictions(dataset_dirs)

    # TODO: separate out calculation of accuracy and cp
    # acc = get_accuracy(dataset_dirs, model)
    # acc = .93972
    acc = 0.845050717034  # for mobilenets-84
    print  'acc:', acc


    lengths = get_length_distribution('../mainstream/image-data/instances/atrium/pedestrian')
    print 'lengths:', lengths
    

    # cp = get_conditional_probability(dataset_dirs, model)
    # cp = 0.1664
    cp = 0.219361147327  # for mobilenets-84
    print  'cp:', cp

    base_folder = "../mainstream-analysis/output/mainstream/frame-rate/"
    # base_folder = "/datasets/BigLearning/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/"
    base_folder += "pedestrian/atrium/"
    # base_folder += "no-afn/train/v2/"
    output_file = base_folder + model_name + "-correlation"
    # runB(dataset_dirs, model, strides, acc, output_file, False, cp)

    output_file = base_folder + model_name + "-dependent-whole"
    # runB(dataset_dirs, model, strides, acc, output_file, False)

    output_file = base_folder + model_name + "-independent-whole"
    # runB(dataset_dirs, model, strides, acc, output_file, True)

    output_file = base_folder + model_name + "-empirical-random"
    runC(dataset_dirs, model, strides, output_file)

    # output_file = base_folder + model_name + "-empirical-temporal"
    #runD(dataset_dirs, model, strides, output_file)
