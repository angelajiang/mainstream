"""
This is a script that can be used to retrain the YOLOv2 model for your own dataset.
"""

import argparse
import CustomCallbacks
import matplotlib.pyplot as plt
import numpy as np
import PIL
import shutil
import tensorflow as tf
from itertools import tee
from keras import backend as K
from keras.layers import Input, Lambda, Conv2D
from keras.models import load_model, Model, save_model
from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping
import os
import sys

sys.path.append("YAD2K")
from yad2k.models.keras_yolo import (preprocess_true_boxes, yolo_body,
                                     yolo_eval, yolo_head, yolo_loss)
from yad2k.utils.draw_boxes import draw_boxes

sys.path.append("YAD2K/util")
import data_utils
from inference import run_inference

# Args
argparser = argparse.ArgumentParser(
    description="Retrain or 'fine-tune' a pretrained YOLOv2 model for your own data.")

argparser.add_argument(
    '-d',
    '--data_path',
    help="path to numpy data file (.npz) containing np.object array 'boxes' and np.uint8 array 'images'",
    default=os.path.join('..', 'DATA', 'underwater_data.npz'))

argparser.add_argument(
    '-a',
    '--anchors_path',
    help='path to anchors file, defaults to yolo_anchors.txt',
    default=os.path.join('~', 'models', 'yad2k_model_data', 'yolo_anchors.txt'))

argparser.add_argument(
    '-c',
    '--classes_path',
    help='path to classes file, defaults to pascal_classes.txt',
    default=os.path.join('..', 'DATA', 'underwater_classes.txt'))

argparser.add_argument(
    '-test',
    '--test_path',
    help='path to test NPZ',
    default=os.path.join(''))

argparser.add_argument(
    '-m',
    '--model_data_path',
    help='Path to pretrained model data',
    default=os.path.join('~', 'models', 'yad2k_model_data'))

argparser.add_argument(
    '-r',
    '--result_path_prefix',
    help='path to result out path',
    default=os.path.join(''))

argparser.add_argument(
    '-p',
    '--model_prefix',
    help='File prefix to save model',
    default='data/yolov2-model-tmp')

argparser.add_argument(
    '-n',
    '--num_frozen',
    help='Number of layers held frozen during training',
    default=0)

argparser.add_argument(
    '-e',
    '--num_epochs',
    help='Number epochs in each stage',
    default=40)

argparser.add_argument(
    '-t',
    '--num_trials',
    help='Number of layers held frozen during training',
    default=1)

argparser.add_argument(
    '-s',
    '--shuffle',
    help='Shuffle input data if True',
    default=1)


# Default anchor boxes
YOLO_ANCHORS = np.array(
    ((0.57273, 0.677385), (1.87446, 2.06253), (3.33843, 5.47434),
     (7.88282, 3.52778), (9.77052, 9.16828)))

def _main(args):
    data_path = os.path.expanduser(args.data_path)
    classes_path = os.path.expanduser(args.classes_path)
    anchors_path = os.path.expanduser(args.anchors_path)
    result_path_prefix = os.path.expanduser(args.result_path_prefix)
    test_path = os.path.expanduser(args.test_path)
    model_prefix = os.path.expanduser(args.model_prefix)
    model_data_path = os.path.expanduser(args.model_data_path)
    num_frozen = int(args.num_frozen)
    num_trials = int(args.num_trials)
    num_epochs = int(args.num_epochs)
    shuffle_input = bool(int(args.shuffle))

    class_names = get_classes(classes_path)

    data = np.load(data_path) # custom data saved as a numpy file.
    #  has 2 arrays: an object array 'boxes' (variable length of boxes in each image)
    #  and an array of images 'images'

    anchors = get_anchors(anchors_path)
    anchors = YOLO_ANCHORS

    # Remove existing result_path_prefix, where all logging will go
    if os.path.exists(result_path_prefix):
       shutil.rmtree(result_path_prefix) 

    log_path_prefix = os.path.join(result_path_prefix, "logs")

    os.mkdir(result_path_prefix)
    os.mkdir(log_path_prefix)
    
    for trial in range(num_trials):

        # Make results paths
        log_path = os.path.join(log_path_prefix, str(num_frozen) + "-" + str(trial))
        os.mkdir(log_path)
        history_path = os.path.join(result_path_prefix, "history-trial" + str(trial))
        accuracy_path = os.path.join(result_path_prefix, "test")
        model_path = model_prefix + "-" + str(num_frozen) + "fr-trial" + str(trial)

        print "Training model:", model_path
        print "TensorBoard logs:", log_path
        print "Training history log:", history_path
        print "Testing accuracy log:", accuracy_path

        # Reprocess data to populate image_data_gen. Sacrifice latency for memory
        image_data_gen, boxes = data_utils.process_data(iter(data['images']),
                                                    data['images'].shape[2],
                                                    data['images'].shape[1],
                                                    data['boxes'],
                                                    dim=608)
        detectors_mask, matching_true_boxes = get_detector_mask(boxes, anchors)

        train(class_names,
              anchors,
              image_data_gen,
              boxes,
              detectors_mask,
              matching_true_boxes,
              model_path,
              model_data_path,
              num_frozen,
              num_epochs,
              log_path=log_path,
              shuffle_input=shuffle_input,
              history_file=history_path
              )

        if test_path != "":
            mAP, f1s, precisions, recalls = run_inference(model_path + ".h5",
                                                          anchors,
                                                          classes_path,
                                                          test_path,
                                                          None,           # output_path
                                                          1,              # mode
                                                          0.5,            # score_threshold
                                                          0.5,            # iou_threshold
                                                          0.5)            # mAP_iou_threshold
            max_i = np.argmax(f1s)
            max_recall = recalls[max_i]
            max_precision = precisions[max_i]
            with open(accuracy_path, "a+") as f:
                line = "%d,%.6g,%.6g,%.6g,%s,%d\n" % (num_frozen,
                                                      mAP,
                                                      max_precision,
                                                      max_recall,
                                                      model_path + ".h5",
                                                      num_epochs)
                f.write(line)


def get_classes(classes_path):
    '''loads the classes'''
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names

def get_anchors(anchors_path):
    '''loads the anchors from a file'''
    if os.path.isfile(anchors_path):
        with open(anchors_path) as f:
            anchors = f.readline()
            anchors = [float(x) for x in anchors.split(',')]
            return np.array(anchors).reshape(-1, 2)
    else:
        Warning("Could not open anchors file, using default.")
        return YOLO_ANCHORS

def get_detector_mask(boxes, anchors):
    '''
    Precompute detectors_mask and matching_true_boxes for training.
    Detectors mask is 1 for each spatial position in the final conv layer and
    anchor that should be active for the given boxes and 0 otherwise.
    Matching true boxes gives the regression targets for the ground truth box
    that caused a detector to be active or 0 otherwise.
    '''
    detectors_mask = [0 for i in range(len(boxes))]
    matching_true_boxes = [0 for i in range(len(boxes))]
    for i, box in enumerate(boxes):
        detectors_mask[i], matching_true_boxes[i] = preprocess_true_boxes(box, anchors, [608, 608])

    return np.array(detectors_mask), np.array(matching_true_boxes)

def create_model(anchors, class_names, model_data_path=".", load_pretrained=True, num_frozen=0):
    '''
    returns the body of the model and the model

    # Params:

    load_pretrained: whether or not to load the pretrained model or initialize all weights

    num_frozen: number of layers whose weights are held frozen during training

    # Returns:

    model_body: YOLOv2 with new output layer

    model: YOLOv2 with custom loss Lambda layer

    '''

    detectors_mask_shape = (19, 19, 5, 1)
    matching_boxes_shape = (19, 19, 5, 5)

    # Create model input layers.
    image_input = Input(shape=(608, 608, 3))
    boxes_input = Input(shape=(None, 5))
    detectors_mask_input = Input(shape=detectors_mask_shape)
    matching_boxes_input = Input(shape=matching_boxes_shape)

    # Create model body.
    yolo_model = yolo_body(image_input, len(anchors), len(class_names))
    topless_yolo = Model(yolo_model.input, yolo_model.layers[-2].output)

    if load_pretrained:
        # Save topless yolo:
        topless_yolo_path = os.path.join(model_data_path, 'yolo-coco_topless.h5')
        if not os.path.exists(topless_yolo_path):
            print("CREATING TOPLESS WEIGHTS FILE")
            yolo_path = os.path.join(model_data_path, 'yolo-coco.h5')
            model_body = load_model(yolo_path)
            model_body = Model(model_body.inputs, model_body.layers[-2].output)
            model_body.save_weights(topless_yolo_path)
        topless_yolo.load_weights(topless_yolo_path)

    num_layers = len(topless_yolo.layers)
    if num_frozen > num_layers:
        print "Cannot freeze", num_frozen, "/", num_layers, "layers"
        sys.exit()

    print "Freezing", num_frozen, "/", num_layers, "layers"
    for i, layer in enumerate(topless_yolo.layers):
        if i < num_frozen:
            layer.trainable = False

    final_layer = Conv2D(len(anchors)*(5+len(class_names)), (1, 1), activation='linear')(topless_yolo.output)

    model_body = Model(image_input, final_layer)

    # Place model loss on CPU to reduce GPU memory usage.
    with tf.device('/cpu:0'):
        # TODO: Replace Lambda with custom Keras layer for loss.
        model_loss = Lambda(
            yolo_loss,
            output_shape=(1, ),
            name='yolo_loss',
            arguments={'anchors': anchors,
                       'num_classes': len(class_names)})([
                           model_body.output, boxes_input,
                           detectors_mask_input, matching_boxes_input
                       ])

    model = Model(
        [model_body.input, boxes_input, detectors_mask_input,
         matching_boxes_input], model_loss)

    return model_body, model

def create_generator(images, boxes, detectors_mask, matching_true_boxes, \
                     batch_size=8, start=0, stop=None):

    if stop == None:
        stop = len(boxes)

    img_batch = []
    a_batch = []
    b_batch = []
    c_batch = []
    y_batch = []

    while(True):
        images, images_copy = tee(images)
        for i, (a,b,c) in enumerate(zip(boxes, detectors_mask, matching_true_boxes)):

            if i >= start and i < stop:
                img = next(images_copy)
                img_batch.append(img)
                a_batch.append(a)
                b_batch.append(b)
                c_batch.append(c)
                y_batch.append(0)

                if len(a_batch) == batch_size:
                    tup = ([np.array(img_batch),
                            np.array(a_batch),
                            np.array(b_batch),
                            np.array(c_batch)],
                            np.array(y_batch))
                    yield tup
                    img_batch = []
                    a_batch = []
                    b_batch = []
                    c_batch = []
                    y_batch = []

def train(class_names, anchors, image_data_gen, boxes, detectors_mask,
          matching_true_boxes, model_prefix, model_data_path, num_frozen, num_epochs,
          log_path="./logs",history_file="history", validation_split=0.1, batch_size=8,
          shuffle_input=True):
    '''
    retrain/fine-tune the model

    logs training with tensorboard

    '''
    logging = TensorBoard(log_dir=log_path)
    best_weights_file = os.path.join(model_prefix + "-best-weights.h5")
    checkpoint = ModelCheckpoint(best_weights_file, monitor='val_loss',
                                 save_weights_only=True, save_best_only=True)
    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=15, verbose=1, mode='auto')

    model_body, model = create_model(anchors, class_names, model_data_path, load_pretrained=True, num_frozen=num_frozen)

    model.compile(
        optimizer='adam', loss={
            'yolo_loss': lambda y_true, y_pred: y_pred
        })  # This is a hack to use the custom loss function in the last layer.

    print "Writing history to", history_file
    loss_callback = CustomCallbacks.Yad2kLossHistory(history_file,
                                                     num_frozen)

    if shuffle_input:
        split_index = int(len(boxes) * 0.9)

        num_training = (split_index - 1) / batch_size
        num_validation = (len(boxes) - split_index) / batch_size

        image_data_gen_1, image_data_gen_2 = tee(image_data_gen)

        gen_train = create_generator(image_data_gen_1, boxes, detectors_mask, matching_true_boxes, stop = split_index, batch_size=batch_size)
        gen_test =  create_generator(image_data_gen_1, boxes, detectors_mask, matching_true_boxes, start = split_index, batch_size=batch_size)

        model.fit_generator(gen_train,
                            epochs=num_epochs,
                            validation_data = gen_test,
                            steps_per_epoch = num_training,
                            validation_steps = num_validation,
                            callbacks=[logging, loss_callback])

        gen_train2 = create_generator(image_data_gen_2, boxes, detectors_mask, matching_true_boxes, stop = split_index, batch_size=batch_size)
        gen_test2 =  create_generator(image_data_gen_2, boxes, detectors_mask, matching_true_boxes, start = split_index, batch_size=batch_size)

        model.fit_generator(gen_train2,
                            epochs=num_epochs,
                            validation_data = gen_test2,
                            steps_per_epoch = num_training,
                            validation_steps = num_validation,
                            callbacks=[logging, loss_callback, checkpoint, early_stopping])
    else:

        image_data = np.array(list(image_data_gen))

        model.fit([image_data, boxes, detectors_mask, matching_true_boxes],
                   np.zeros(len(image_data)),
                   validation_split=0.1,
                   batch_size=8,
                   epochs=num_epochs,
                   shuffle=False,
                   callbacks=[logging])

        model.fit([image_data, boxes, detectors_mask, matching_true_boxes],
                   np.zeros(len(image_data)),
                   validation_split=0.1,
                   batch_size=8,
                   epochs=num_epochs,
                   shuffle=False,
                   callbacks=[logging, checkpoint, early_stopping])


    #sess = K.get_session()
    #graph_def = sess.graph.as_graph_def()
    #tf.train.write_graph(graph_def,
    #                     logdir='.',
    #                     name=model_prefix+".pb",
    #                     as_text=False)
    #saver = tf.train.Saver()
    #saver.save(sess, model_prefix+'.ckpt', write_meta_graph=True)

    #model_body.save_weights(model_prefix+"_weights.h5")
    model_body.load_weights(best_weights_file)
    save_model(model_body, model_prefix+".h5", overwrite=True)

if __name__ == '__main__':
    args = argparser.parse_args()
    _main(args)
