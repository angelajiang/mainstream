import sys
sys.path.append('util')
import dataset
import ConfigParser
sys.path.append('training')
import FineTunerFast as ft
import net
import pickle
import pprint as pp
import tensorflow as tf
import numpy as np


def predict(model_path, dataset_dir):
    model, tags = net.load(model_path)
    data_X, data_y, tags = dataset.dataset(dataset_dir, 299)

    net.compile(model)
    predictions = []
    for d in data_X:
        X = np.expand_dims(d, axis=0)
        prediction = model.predict(X)
        predictions.append(prediction[0])
    return predictions

if __name__ == "__main__":
    model_path_h5, dataset_dir = sys.argv[1:]
    predictions = predict(model_path_h5, dataset_dir)
    print predictions
