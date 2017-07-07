import sys
sys.path.append('../util')
import Data
import ConfigParser
import json
import net
import numpy as np
import pprint as pp
import os.path
import time

from collections import defaultdict

# It's very important to put this import before keras,
# as explained here: Loading tensorflow before scipy.misc seems to cause imread to fail #1541
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

    def __init__(self, config_file_path, data_directory, history_file, model_file_prefix):

        np.random.seed(1337)

        config_parserr = ConfigParser.RawConfigParser()   
        config_parserr.read(config_file_path)

        self.data_directory = data_directory

        self.history_file = history_file
        self.model_file_prefix = model_file_prefix

        self.n = int(config_parserr.get('finetune-config', 'n'))
        self.batch_size = int(config_parserr.get('finetune-config', 'batch_size'))
        self.max_nb_epoch = int(config_parserr.get('finetune-config', 'max_nb_epoch'))
        self.num_mega_epochs = int(config_parserr.get('finetune-config', 'num_mega_epochs'))
        self.patience = int(config_parserr.get('finetune-config', 'patience'))
        self.data_augmentation = bool(int(config_parserr.get('finetune-config', 'data_augmentation')))
        self.heavy_augmentation = bool(int(config_parserr.get('finetune-config', 'heavy_augmentation')))
        self.weights = str(config_parserr.get('finetune-config', 'weights'))
        optimizer_name = str(config_parserr.get('finetune-config', 'optimizer'))
        decay = float(config_parserr.get('finetune-config', 'decay'))
        lr = float(config_parserr.get('finetune-config', 'learning-rate'))                          # Should be low for finetuning

        # sets self.dataset.datagen, self.dataset.X_train, self.dataset.Y_train, self.dataset.X_test, self.dataset.Y_test
        self.dataset = Data.Data(data_directory, self.n)

        if self.weights == "imagenet":
            self.weights = "imagenet"
        else:
            self.weights = None

        if optimizer_name == "adam":
            self.optimizer = Adam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=decay)
        elif optimizer_name == "adamax":
            self.optimizer = Adamax(lr=l4, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=decay)
        elif optimizer_name == "nadam":
            self.optimizer = Nadam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=decay)
        elif optimizer_name == "rmsprop":
            self.optimizer = RMSprop(lr=lr, rho=0.9, epsilon=1e-08, decay=decay)
        elif optimizer_name == "sgd":
            self.optimizer = SGD(lr=lr, momentum=0.0, decay=decay, nesterov=False)
        else:
            print "[ERROR] Didn't recognize optimizer", optimizer_name
	    sys.exit(-1)

        self.init_model()       # sets self.model, self.tags

        self.config_parser = config_parserr

    def init_model(self):
        print "[WARNING] Generating new model"
        model = net.build_model(self.dataset.nb_classes, self.weights)
        model.compile(optimizer=self.optimizer, loss='categorical_crossentropy', metrics=["accuracy"])
        self.model = model

    def evaluate(self, model):
        Y_pred = model.predict(self.dataset.X_test, batch_size=self.batch_size)
        y_pred = np.argmax(Y_pred, axis=1)
        accuracy = float(np.sum(self.dataset.y_test==y_pred)) / len(self.dataset.y_test)
        return accuracy

    def finetune(self, num_train):

        num_layers = len(self.model.layers)
        num_frozen = num_layers - num_train
        if (num_frozen < 0):
            print "[ERROR]: num_train > num_layers"
            return -1

        print "Num_layers:", num_layers, " num frozen:", num_frozen
        for layer in self.model.layers[:num_frozen]:
           layer.trainable = False
        for layer in self.model.layers[num_frozen:]:
           layer.trainable = True

        # we need to recompile the model for these modifications to take effect
        # we use SGD with a low learning rate
        self.model.compile(optimizer=self.optimizer, loss='categorical_crossentropy', metrics=["accuracy"])

        # we train our model again (this time fine-tuning the top 2 inception blocks
        # alongside the top Dense layers

        # Instantiate a callback that records intermediate accuracy into history_file

        self.history = CustomCallbacks.LossHistory(self.history_file, num_train, self.dataset.X_test, self.dataset.Y_test)
        callbacks = [
            self.history,
            keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=self.patience, verbose=1, mode='auto')
        ]

        if self.data_augmentation:
            for i in range(1, self.num_mega_epochs + 1):
                print "mega-epoch %d/%d" % (i, self.num_mega_epochs)
                self.model.fit_generator(self.datagen.flow(self.dataset.X_train, self.dataset.Y_train, batch_size=self.batch_size, shuffle=False),
                        samples_per_epoch=self.dataset.X_train.shape[1],
                        nb_epoch=self.max_nb_epoch,
                        validation_data=self.datagen.flow(self.dataset.X_test, self.dataset.Y_test, batch_size=self.batch_size),
                        callbacks=callbacks,
                        nb_val_samples=self.dataset.X_test.shape[0]
                        )

        else:
            for i in range(1, self.num_mega_epochs + 1):
                print "mega-epoch %d/%d" % (i, self.num_mega_epochs)

                 #   # train the model on the new data for a few epochs
                loss = self.model.fit(self.dataset.X_train, self.dataset.Y_train,
                                      batch_size=self.batch_size,
                                      nb_epoch=self.max_nb_epoch,
                                      validation_split=0.1,
                                      callbacks=callbacks,
                                      shuffle=False)
        net.save_pb(self.model, self.model_file_prefix)

        accuracy = self.evaluate(self.model)
        print "[finetune] accuracy:" , accuracy
        return accuracy

    def print_config(self):
        d = dict(self.config_parser.items("finetune-config"))
        pp.pprint(d)


