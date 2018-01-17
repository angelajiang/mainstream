import json

import sys
import tensorflow as tf 
from keras import backend as K
from keras.applications.inception_v3 import InceptionV3
from keras.applications.resnet50 import ResNet50
from keras.applications.mobilenet import MobileNet
from keras.models import Model, model_from_json, save_model
from keras.layers import Dense, GlobalAveragePooling2D


# create the base pre-trained model
def build_model(net_architecture, nb_classes):
    K.set_learning_phase(1) 

    # Set neural net architecture
    if net_architecture == "InceptionV3":
        base_model = InceptionV3(weights="imagenet", include_top=False)
    elif net_architecture == "ResNet50":
        base_model = ResNet50(weights="imagenet", include_top=False)
    elif net_architecture == "MobileNet":
        base_model = MobileNet(weights="imagenet", include_top=False)
    else:
        print("[ERROR] Didn't recognize net ", net_architecture)
        sys.exit(-1)

    x = base_model.output
    x = GlobalAveragePooling2D()(x)                             # Pooling layer
    x = Dense(1024, activation='relu')(x)                       # FC layer
    predictions = Dense(nb_classes, activation='softmax')(x)    # Logistic layer

    model = Model(input=base_model.input, output=predictions)

    compile(model)
    return model

def save_h5(model, tags, prefix):
    model.save_weights(prefix+".h5")
    #save_model(model, prefix+".h5", overwrite=True)
    model_json = model.to_json()
    with open(prefix+".json", "w") as json_file:
        json_file.write(model_json)
    with open(prefix+"-labels.json", "w") as json_file:
        json.dump(tags, json_file)

def save_pb(mem_model, prefix):
    sess = K.get_session()
    graph_def = sess.graph.as_graph_def()
    tf.train.write_graph(graph_def,
                         logdir='.',
                         name=prefix+'.pb',
                         as_text=False)
    saver = tf.train.Saver()
    saver.save(sess, prefix+'.ckpt', write_meta_graph=True)
    print("[net]", prefix+'.pb')

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
    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy',
                  metrics=["accuracy"])
