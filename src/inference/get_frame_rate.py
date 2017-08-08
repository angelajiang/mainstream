import sys
sys.path.append('src/inference')
import inference_h5
import os
from collections import defaultdict


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

def get_length_distribution(base_dir):
    # Returns list of number of files in each subdirectory of base_dir
    data_files = get_dataset(base_dir)
    sizes = [len(v) for k, v in data_files.iteritems()]
    return sizes

def get_confidence_distribution(dataset_dir, model_path):
    # Returns list of list of classification probability of running inference
    # using model of each image subdirectory of base_dir
    # ex) [[0.5, 0.8, 0.5], [0.6, 0.8, 0.7, 0.6]
    predictions = inference_h5.predict(model_path, dataset_dir)
    return predictions

if __name__ == "__main__":
    '''
    sizes = get_length_distribution(base_dir)
    '''

    dataset_dir = sys.argv[1]
    model_path = sys.argv[2]
    predictions = get_confidence_distribution(dataset_dir, model_path)
    for prediction in predictions:
        print(prediction[1])
