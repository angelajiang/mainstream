import sys
sys.path.append('src/util')
import net
import pprint as pp
import tensorflow as tf


def get_weights(model_path):

    model_ckpt_path = model_path + ".ckpt"
    with tf.Session() as sess:
        new_saver = tf.train.import_meta_graph(model_ckpt_path + ".meta")
        new_saver.restore(sess, model_ckpt_path)
        variables_names = [v.name for v in tf.trainable_variables()]
        values = sess.run(variables_names)
        all_weights = {}
        for k, v in zip(variables_names, values):
            all_weights[k] = v
    return all_weights

if __name__ == "__main__":
    model_path_pb = sys.argv[1]
    weights_map = get_weights(model_path_pb)
    for layer, weights in weights_map.iteritems():
        print "---------------", layer, "---------------"
        pp.pprint(weights)
