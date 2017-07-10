import sys
sys.path.append('src/util')
import net
import pprint as pp
import tensorflow as tf


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

def get_weights(model_path):
    '''
    # load tf graph
    tf_model, tf_input, tf_output = load_graph(model_path)

    # Create tensors for model input and output
    x = tf_model.get_tensor_by_name(tf_input)
    y = tf_model.get_tensor_by_name(tf_output)


    with tf.Session(graph=tf_model) as sess:
        graph_def = sess.graph.as_graph_def()
        #print [n.name for n in tf.get_default_graph().as_graph_def().node]
        op = tf.get_default_graph().get_operation_by_name("prefix/conv2d_1/kernel")
        print op.values
        '''

    with tf.Session() as sess:
        new_saver = tf.train.import_meta_graph(model_path + ".meta")
        new_saver.restore(sess, model_path)
        variables_names = [v.name for v in tf.trainable_variables()]
        values = sess.run(variables_names)
        for k, v in zip(variables_names, values):
            print "----------------", k, "----------------"
            print "Shape: ", v.shape
            print v

    return {}

if __name__ == "__main__":
    model_path_pb = sys.argv[1]
    weights_map = get_weights(model_path_pb)
    for layer, weights in weights_map.iteritems():
        print "---------------", layer, "---------------"
        pp.pprint(weights)
