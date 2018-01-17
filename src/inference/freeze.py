import sys
import tensorflow as tf
from tensorflow.python.tools import freeze_graph

def freeze(model_prefix):

    new_graph = tf.Graph()
    with tf.Session(graph=new_graph) as sess:
        new_saver = tf.train.import_meta_graph(model_prefix + ".ckpt.meta")
        new_saver.restore(sess, model_prefix + ".ckpt")
        graph_def = sess.graph.as_graph_def()

        freeze_graph.freeze_graph(model_prefix + ".pb",
                                  "",
                                  True,
                                  model_prefix + ".ckpt",
                                  #'init_1',
                                  'Gather_2', # YAD2K-full
                                  #'conv2d_24/BiasAdd', # YAD2K
                                  #'dense_2/Softmax',  # Keras master InceptionV3
                                  #'act_softmax/div',  # Keras master InceptionV3 imagenet
                                  'save/restore_all',
                                  'save/Const:0',
                                  model_prefix + '-frozen.pb',
                                  True,
                                  "")

if __name__ == "__main__":
    model_prefix = sys.argv[1]
    freeze(model_prefix)

