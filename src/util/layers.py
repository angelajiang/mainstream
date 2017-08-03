import sys
sys.path.append('src/util')
from keras.models import load_model
from keras.models import load_model
from keras.applications.mobilenet import relu6, DepthwiseConv2D
import net

def get_mobilenet_layers(model_path):
    # In training save model in the following way:
    #save_model(model, prefix+".h5", overwrite=True)
    #from keras.models import Model, model_from_json, save_model
    model = load_model(model_path, custom_objects={
                                        'relu6': relu6,
                                        'DepthwiseConv2D': DepthwiseConv2D})

    count = 0 
    for layer in model.layers:
        print str(count) + "," + layer.get_config()["name"]
        count += 1

def get_layers(model_path):
    model, tags = net.load(model_path)
    net.compile(model)

    print len(model.layers)
    count = 0 
    for layer in model.layers:
        print count + "," + layer.get_config()["name"]
        count += 1

if __name__ == "__main__":
    model_path_h5 = sys.argv[1]
    get_mobilenet_layers(model_path_h5)
