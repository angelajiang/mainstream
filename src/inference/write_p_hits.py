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

def get_detection_probability(dataset_dirs, model_path, strides, within_frames_slo):
    p_hits = {}
    for dataset_dir in dataset_dirs:
        print "----------------------", dataset_dir, "------------------------"
        predictions = inference_h5.predict(model_path, dataset_dir)
        print predictions

        for stride in strides:
            for slo in within_frames_slo:

                identifications = sum([1 for p in predictions if p[1] >= 0.5]) 
                p_identified = identifications / float(len(predictions))

                d = float(min(slo, len(predictions)))
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

def get_accuracy(dataset_dirs, model_path):
    print "----------------------", model_path, "------------------------"
    for dataset_dir in dataset_dirs:
        predictions = inference_h5.predict(model_path, dataset_dir)
        identifications = sum([1 for p in predictions if p[1] >= 0.5]) 
        p_identified = identifications / float(len(predictions))
        print dataset_dir, p_identified

def run(dataset_dirs, model_path, strides, within_frames_slo, output_file):
    p_hits = get_detection_probability(dataset_dirs,
                                       model_path,
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

    #strides = range(1, 301, 1)
    #within_frames_slo = [1, 10, 20, 30, 40, 50]

    strides = [1]
    within_frames_slo = [1]

    model_path = "/users/ahjiang/models/nsdi/train/inception/train-imagenet-noafn1245-0"
    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn1245/trains-0"
    get_accuracy(dataset_dirs, model_path)
    #run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/nsdi/train/inception/train-imagenet-noafn1245-165"
    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn1245/trains-0"
    get_accuracy(dataset_dirs, model_path)
    #run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

