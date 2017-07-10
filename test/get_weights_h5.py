import sys
sys.path.append('src/util')
import net
import pprint as pp
import tensorflow as tf


def get_weights(model_path):
    model, tags = net.load(model_path)
    net.compile(model)
    weights_map = {}
    for layer in model.layers:
        weights = layer.get_weights()
        weights_map[layer.name] = weights
    return weights_map

if __name__ == "__main__":
    model_path_h5 = sys.argv[1]
    weights_map = get_weights(model_path_h5)
    for layer, weights in weights_map.iteritems():
        print "---------------", layer, "---------------"
        pp.pprint(weights)
