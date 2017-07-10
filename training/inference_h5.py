import sys
sys.path.append('../util')
import dataset
import ConfigParser
import FineTunerFast as ft
import net
import pickle
import pprint as pp
import tensorflow as tf
import numpy as np

def predict(model_path, dataset_dir):
    # load tf graph
    model, tags = net.load(model_path)

    data_X, data_y, tags = dataset.dataset(dataset_dir, 299)
    data_X = [d.reshape(299, 299, 3) for d in data_X]

    net.compile(model)
    for d in data_X:
        X = np.expand_dims(d, axis=0)
        outs = model.predict(X)
        print outs
    return

if __name__ == "__main__":
    model_path_pb, dataset_dir = sys.argv[1:]
    predict(model_path_pb, dataset_dir)

