import dataset
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
import numpy as np

class DataSet:

    def __init__(self, data_directory, n):

        self.data_directory = data_directory
        self.n = n

        X, y, tags = dataset.dataset(self.data_directory, self.n)
        self.nb_classes = len(tags)

        sample_count = len(y)
        train_size = sample_count * 4 // 5
        X_train = X[:train_size]
        y_train = y[:train_size]
        Y_train = np_utils.to_categorical(y_train, self.nb_classes)
        X_test  = X[train_size:]
        y_test  = y[train_size:]
        Y_test = np_utils.to_categorical(y_test, self.nb_classes)

        X_train = [x.reshape(224, 224, 3) for x in X_train]
        X_test = [x.reshape(224, 224, 3) for x in X_test]

        self.datagen = ImageDataGenerator(
            featurewise_center=False,
            samplewise_center=False,
            featurewise_std_normalization=False,
            samplewise_std_normalization=False,
            zca_whitening=False,
            rotation_range=0,
            width_shift_range=0.125,
            height_shift_range=0.125,
            horizontal_flip=True,
            vertical_flip=False,
            fill_mode='nearest')

        self.X_train = np.array(X_train)
        self.X_test = np.array(X_test)
        self.Y_train = Y_train
        self.Y_test = Y_test
        self.y_train = y_train
        self.y_test = y_test
        self.tags = tags
