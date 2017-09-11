import tensorflow as tf
import sys
from tensorflow.python.platform import gfile
import pprint as pp

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "</path/to/pb.pb> <path/to/logdir>"
        sys.exit(-1)
    model_filename = sys.argv[1]
    LOGDIR = sys.argv[2]

    with tf.Session() as sess:
        with gfile.FastGFile(model_filename, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            g_in = tf.import_graph_def(graph_def)

            # Print op names
            ops = sess.graph.get_operations()
            names = [op.name for op in ops]
            pp.pprint(names)
    train_writer = tf.summary.FileWriter(LOGDIR)
    train_writer.add_graph(sess.graph)
    print "python -m tensorflow.tensorboard --logdir=" + LOGDIR
