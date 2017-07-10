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
                                  'dense_2/Softmax',
                                  'save/restore_all',
                                  'save/Const:0',
                                  model_prefix + '-frozen.pb',
                                  True,
                                  "")

if __name__ == "__main__":
    model_prefix = sys.argv[1]
    freeze(model_prefix)

