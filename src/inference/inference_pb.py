import sys
sys.path.append('util')
import dataset
import ConfigParser
sys.path.append('training')
import FineTunerFast as ft
import math
import pickle
import pprint as pp
import tensorflow as tf
import numpy as np

def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a
    # graph_def into the current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            name="prefix", 
            op_dict=None, 
            producer_op_list=None
        )

    input_name = graph.get_operations()[0].name+':0'
    output_name = graph.get_operations()[-1].name+':0'

    return graph, input_name, output_name

def predict(model_path, dataset_dir):
    # load tf graph
    tf_model,tf_input,tf_output = load_graph(model_path)

    # Create tensors for model input and output
    x = tf_model.get_tensor_by_name(tf_input)
    y = tf_model.get_tensor_by_name(tf_output)

    # Get data
    data_X, data_y, tags = dataset.dataset(dataset_dir, 299)

    with tf.Session(graph=tf_model) as sess:

        graph_def = sess.graph.as_graph_def()

        tf.summary.image('input', x, max_outputs=7)
        writer = tf.summary.FileWriter("/tmp/log/")
        writer.add_graph(sess.graph)
        merged_summary = tf.summary.merge_all()

        for i, d in enumerate(data_X):
            s, y_out = sess.run([merged_summary, y], feed_dict={x: [d]})
            writer.add_summary(s, i)
            print y_out

    return

if __name__ == "__main__":
    model_path_pb, dataset_dir = sys.argv[1:]
    predict(model_path_pb, dataset_dir)
