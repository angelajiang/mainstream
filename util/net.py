
import json

import sys
import tensorflow as tf
from keras import backend as K
from keras.applications.inception_v3 import InceptionV3
from keras.models import Model, model_from_json
from keras.layers import Dense, GlobalAveragePooling2D


# create the base pre-trained model
def build_model(nb_classes, weights="imagenet"):
    base_model = InceptionV3(weights=weights, include_top=False)

    # add a global spatial average pooling layer
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    # let's add a fully-connected layer
    x = Dense(1024, activation='relu')(x)
    # and a logistic layer
    predictions = Dense(nb_classes, activation='softmax')(x)

    # this is the model we will train
    model = Model(input=base_model.input, output=predictions)

    #base_model -> modelA
    #modelA = Model(input=base_model.output, output=predictions)

    # first: train only the top layers (which were randomly initialized)
    # i.e. freeze all convolutional InceptionV3 layers
    for layer in base_model.layers:
        layer.trainable = False

    # compile the model (should be done *after* setting layers to non-trainable)
    print "starting model compile"
    compile(model)
    print "model compile done"
    return model

def save_h5(model, tags, prefix):
    model.save_weights(prefix+".h5")
    # serialize model to JSON
    model_json = model.to_json()
    with open(prefix+".json", "w") as json_file:
        json_file.write(model_json)
    with open(prefix+"-labels.json", "w") as json_file:
        json.dump(tags, json_file)

def save_pb(mem_model, prefix):
    with tf.Session() as sess:
        graph_def = K.get_session().graph
	tf.train.write_graph(graph_def, logdir='.', name=prefix+'.pb', as_text=False)
	saver = tf.train.Saver()
        print "[net]", prefix+'.pb'
	#saver.save(sess, prefix+'model.ckpt')

def load(prefix):
    # load json and create model
    with open(prefix+".json") as json_file:
        model_json = json_file.read()
    model = model_from_json(model_json)
    # load weights into new model
    model.load_weights(prefix+".h5")
    with open(prefix+"-labels.json") as json_file:
        tags = json.load(json_file)
    return model, tags

def compile(model):
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=["accuracy"])
