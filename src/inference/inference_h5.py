import sys
sys.path.append('src/util')
import dataset
import ConfigParser
sys.path.append('src/training')
import FineTunerFast as ft
import net
import pickle
import pprint as pp
import tensorflow as tf
import numpy as np


class Model(object):
    """docstring for Model"""
    def __init__(self, model_path):
        super(Model, self).__init__()
        self.model, self.tags = net.load(model_path)
        net.compile(self.model)
        self.dim = 224 if 'mobilenets' in model_path else 299
        print 'Tags', self.tags

    def predict(self, dataset_dir):
        data_X, data_y, tags = dataset.dataset(dataset_dir, self.dim, False)
        print dataset_dir, "shape", data_X.shape
        if data_X.size == 0:
            return []
        return self.model.predict(data_X)

    def predict_by_tag(self, dataset_dir):
        data_X = dataset.dataset_with_root_dir(dataset_dir, self.dim)
        tag_index = [i for i, t in enumerate(tags) if t == tag][0]
        print tags

        predictions = []
        for d in data_X:
            X = np.expand_dims(d, axis=0)
            prediction = (self.model.predict(X)).tolist()[0]
            argmax = prediction.index(max(prediction))
            if argmax == tag_index:
                predictions.append(1)
            else:
                predictions.append(0)
        return predictions


def predict_with_dataset(model_path, dataset):
    model, tags = net.load(model_path)

    data_X = dataset.X
    data_y = dataset.y

    net.compile(model)
    predictions = []
    for d in data_X:
        X = np.expand_dims(d, axis=0)
        prediction = model.predict(X)
        predictions.append(prediction[0])
    return predictions

def predict(model_path, dataset_dir):
    model, tags = net.load(model_path)
    print tags
    # Inception
    # data_X, data_y, tags = dataset.dataset(dataset_dir, 299, False)
    # MobileNets
    data_X, data_y, tags = dataset.dataset(dataset_dir, 224, False)

    net.compile(model)
    predictions = []
    # print 'shape', data_X.shape
    # prediction = model.predict(data_X)
    # print prediction.shape
    # prediction = prediction[:, 0]
    for d in data_X:
        X = np.expand_dims(d, axis=0)
        prediction = model.predict(X)
        predictions.append(prediction[0])
    return predictions

def predict_by_tag(model_path, dataset_dir, tag):
    model, tags = net.load(model_path)
    tag_index = [i for i, t in enumerate(tags) if t == tag][0]
    # Inception
    # data_X = dataset.dataset_with_root_dir(dataset_dir, 299)
    # MobileNets
    data_X = dataset.dataset_with_root_dir(dataset_dir, 224)
    print tags

    net.compile(model)
    predictions = []
    for d in data_X:
        X = np.expand_dims(d, axis=0)
        prediction = (model.predict(X)).tolist()[0]
        argmax = prediction.index(max(prediction))
        if argmax == tag_index:
            predictions.append(1)
        else:
            predictions.append(0)
    return predictions

if __name__ == "__main__":
    model_path_h5, dataset_dir = sys.argv[1:]
    predictions = predict(model_path_h5, dataset_dir)
    for predict in predictions:
        print predict
