import dataset
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
import numpy as np

class Data:

    def __init__(self, data_directory, data_test_directory, n):

        print data_directory, data_test_directory

        self.data_directory = data_directory
        self.n = n

        X, y, tags = dataset.dataset(self.data_directory, self.n)
        self.nb_classes = len(tags)

        if data_test_directory == None:
            sample_count = len(y)
            train_size = sample_count * 4 // 5
            X_train = X[:train_size]
            y_train = y[:train_size]

            X_test  = X[train_size:]
            y_test  = y[train_size:]

        else:
            X_train = X
            y_train = y

            X_test, y_test, test_tags = dataset.dataset(data_test_directory, n)
            nb_classes_test = len(test_tags)
            assert nb_classes_test == self.nb_classes

        Y_train = np_utils.to_categorical(y_train, self.nb_classes)
        Y_test = np_utils.to_categorical(y_test, self.nb_classes)
        X_train = [x.reshape(n, n, 3) for x in X_train]
        X_test = [x.reshape(n, n, 3) for x in X_test]

	self.datagen = ImageDataGenerator(
	    featurewise_center=False,
	    samplewise_center=False,
	    featurewise_std_normalization=False,
	    samplewise_std_normalization=False,
	    zca_whitening=False,
	    rotation_range=45,
	    width_shift_range=0.25,
	    height_shift_range=0.25,
	    horizontal_flip=True,
	    vertical_flip=True,
	    zoom_range=0.5,
	    channel_shift_range=0.5,
	    fill_mode='nearest')

        self.X = X
        self.y = y
        self.X_train = np.array(X_train)
        self.X_test = np.array(X_test)
        self.Y_train = Y_train
        self.Y_test = Y_test
        self.y_train = y_train
        self.y_test = y_test
        self.tags = tags

