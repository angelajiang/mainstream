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

    dataset_dirs = ["/users/ahjiang/image-data/instances/train_images_resized/a/",
                    "/users/ahjiang/image-data/instances/train_images_resized/b/",
                    "/users/ahjiang/image-data/instances/train_images_resized/c/",
                    "/users/ahjiang/image-data/instances/train_images_resized/f/",
                    "/users/ahjiang/image-data/instances/train_images_resized/g/",
                    "/users/ahjiang/image-data/instances/train_images_resized/h/",
                    "/users/ahjiang/image-data/instances/train_images_resized/i/",
                    "/users/ahjiang/image-data/instances/train_images_resized/j/",
                    "/users/ahjiang/image-data/instances/train_images_resized/k/",
                    "/users/ahjiang/image-data/instances/train_images_resized/m/",
                    "/users/ahjiang/image-data/instances/train_images_resized/n/",
                    "/users/ahjiang/image-data/instances/train_images_resized/o/",
                    "/users/ahjiang/image-data/instances/train_images_resized/p/",
                    "/users/ahjiang/image-data/instances/train_images_resized/q/",
                    "/users/ahjiang/image-data/instances/train_images_resized/r/",
                    "/users/ahjiang/image-data/instances/train_images_resized/t/",
                    "/users/ahjiang/image-data/instances/train_images_resized/u/",
                    "/users/ahjiang/image-data/instances/train_images_resized/v/"]

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
    within_frames_slo = [1, 50, 100, 150, 200, 250, 300]

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-313"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-313"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-280"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-280"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-0"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-0"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-4"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-4"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-17"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-17"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-18"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-18"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-41"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-41"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-87"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-87"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-165"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-165"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-197"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-197"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-229"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-229"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-249"
    output_file = "/users/ahjiang/src/mainstream/log/frame-rate/no-afn/train/frame-rate-trains-no-afn-249"
    run(dataset_dirs, model_path, strides, within_frames_slo, output_file)


