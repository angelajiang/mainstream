import sys
sys.path.append('src/util')
import net
import pprint as pp
import tensorflow as tf

from keras.models import load_model


def get_weights(model_path, num_layers = -1):
    model, tags = net.load(model_path)
    net.compile(model)
    weights_map = {}
    if num_layers < 0:
        num_layers = len(model.layers)
    for layer in model.layers[:num_layers]:
        weights = layer.get_weights()
        weights_map[layer.name] = weights
    return weights_map

def get_weights_yad2k(model_path, num_layers = -1):
    model = load_model(model_path, compile=False)
    weights_map = {}
    if num_layers < 0:
        num_layers = len(model.layers)
    for layer in model.layers[:num_layers]:
        weights = layer.get_weights()
        weights_map[layer.name] = weights
    return weights_map

if __name__ == "__main__":
    model_path_h5 = sys.argv[1]
    weights_map = get_weights(model_path_h5)
    for layer, weights in weights_map.iteritems():
        print "---------------", layer, "---------------"
        pp.pprint(weights)
