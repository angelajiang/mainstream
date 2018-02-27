import sys
sys.path.append('src/util')
import Data
import ConfigParser
import json
import net
import numpy as np
import pprint as pp
import os.path
import time

from collections import defaultdict

# It's very important to put this import before keras, as explained here:
# Loading tensorflow before scipy.misc seems to cause imread to fail #1541
# https://github.com/tensorflow/tensorflow/issues/1541
import scipy.misc

import CustomCallbacks
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD, Adam, Nadam, RMSprop, Adamax
from keras import backend as K
from keras.utils import np_utils

import dataset


class FineTunerFast:

    def __init__(self, config_file_path, history_file, model_file_prefix,
                 data_directory, data_test_directory=None):

        np.random.seed(1337)

        # Set up config
        config_parserr = ConfigParser.RawConfigParser()
        config_parserr.read(config_file_path)
        self.config_parser = config_parserr

        # Set up dataset
        self.n = int(config_parserr.get('finetune-config', 'n'))
        self.dataset = Data.Data(data_directory, data_test_directory, self.n)

        # Get model configuration
        self.net = str(config_parserr.get('finetune-config', 'net'))
        optimizer_name = str(config_parserr.get('finetune-config', 'optimizer'))
        decay = float(config_parserr.get('finetune-config', 'decay'))
        lr = float(config_parserr.get('finetune-config', 'learning-rate'))

        # Get training configuration
        self.batch_size = int(config_parserr.get('finetune-config', 'batch_size'))
        self.max_nb_epoch = int(config_parserr.get('finetune-config', 'max_nb_epoch'))
        self.patience = int(config_parserr.get('finetune-config', 'patience'))
        self.data_augmentation = bool(int(config_parserr.get('finetune-config', 'data_augmentation')))
        self.heavy_augmentation = bool(int(config_parserr.get('finetune-config', 'heavy_augmentation')))

        # Get persistence configuration
        self.history_file = history_file
        self.model_file_prefix = model_file_prefix

        # Set self.optimizer
        if optimizer_name == "adam":
            self.optimizer = \
                Adam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=decay)
        elif optimizer_name == "adamax":
            self.optimizer = \
                Adamax(lr=l4, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=decay)
        elif optimizer_name == "nadam":
            self.optimizer = \
                Nadam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=decay)
        elif optimizer_name == "rmsprop":
            self.optimizer = \
                RMSprop(lr=lr, rho=0.9, epsilon=1e-08, decay=decay)
        elif optimizer_name == "sgd":
            self.optimizer = \
                SGD(lr=lr, momentum=0.0, decay=decay, nesterov=False)
        else:
            print "[ERROR] Didn't recognize optimizer", optimizer_name
	    sys.exit(-1)

        self.init_model()       # Sets self.model

    def init_model(self):
        model = net.build_model(self.net, self.dataset.nb_classes)
        model.compile(optimizer=self.optimizer,
                      loss='categorical_crossentropy',
                      metrics=["accuracy"])
        self.model = model

    def evaluate(self, model):
        Y_pred = model.predict(self.dataset.X_test, batch_size=self.batch_size)
        y_pred = np.argmax(Y_pred, axis=1)
        top1_accuracy = float(np.sum(self.dataset.y_test==y_pred)) \
                            / len(self.dataset.y_test)
        fprs = []
        for tag in range(len(self.dataset.tags)):
            negatives = [i for i, x in enumerate(self.dataset.y_test) if x != tag]
            positives = [1 for i in negatives if y_pred[i] == tag]
            fpr = sum(positives) / float(len(negatives))
            fprs.append(fpr)
            print tag, fpr

        average_fpr = sum(fprs) / float(len(fprs))

        return top1_accuracy, average_fpr

    def finetune(self, num_frozen):

        print "Layers frozen:", num_frozen , "/" , len(self.model.layers)
        for layer in self.model.layers[:num_frozen]:
           layer.trainable = False
        for layer in self.model.layers[num_frozen:]:
           layer.trainable = True

        # Recompile the model for these modifications to take effect
        self.model.compile(optimizer=self.optimizer,
                           loss='categorical_crossentropy',
                           metrics=["accuracy"])

        callbacks = [
            # Record intermediate accuracy into self.history_file
            CustomCallbacks.LossHistory(self.history_file,
                                        num_frozen,
                                        self.dataset.X_test,
                                        self.dataset.Y_test),
            keras.callbacks.EarlyStopping(monitor='val_loss',
                                          min_delta=0,
                                          patience=self.patience,
                                          verbose=1,
                                          mode='auto')
        ]

        if self.data_augmentation:
            self.model.fit_generator(
                    self.dataset.datagen.flow(self.dataset.X_train,
                                              self.dataset.Y_train,
                                              batch_size=self.batch_size,
                                              shuffle=False),
                    samples_per_epoch=self.dataset.X_train.shape[1],
                    nb_epoch=self.max_nb_epoch,
                    validation_data=
                        self.dataset.datagen.flow(self.dataset.X_test,
                                                  self.dataset.Y_test,
                                                  batch_size=self.batch_size),
                    callbacks=callbacks,
                    nb_val_samples=self.dataset.X_test.shape[0])

        else:
            self.model.fit(self.dataset.X_train,
                           self.dataset.Y_train,
                           batch_size=self.batch_size,
                           nb_epoch=self.max_nb_epoch,
                           validation_split=0.1,
                           callbacks=callbacks,
                           shuffle=False)

        net.save_pb(self.model, self.model_file_prefix)
        net.save_h5(self.model, self.dataset.tags, self.model_file_prefix)

        top1_accuracy, average_fpr = self.evaluate(self.model)
        print  "[finetune] Acc: {acc}, FPR: {fpr}".format(**{
                        "acc": top1_accuracy,
                        "fpr": average_fpr})

        return top1_accuracy, average_fpr

    def print_config(self):
        d = dict(self.config_parser.items("finetune-config"))
        pp.pprint(d)
