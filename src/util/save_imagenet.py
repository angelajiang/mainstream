import sys
sys.path.append('src/util')
sys.path.append('src/inference')
import freeze
import net
import freeze
import tensorflow as tf 
from keras import backend as K
from keras.applications.inception_v3 import InceptionV3
from keras.applications.resnet50 import ResNet50
from keras.applications.mobilenet import MobileNet

def save_imagenet(net_architecture, prefix):

    K.set_learning_phase(1) 

    # Set neural net architecture
    if net_architecture == "InceptionV3":
        model = InceptionV3(weights="imagenet", include_top=True)
    elif net_architecture == "ResNet50":
        model = ResNet50(weights="imagenet", include_top=True)
    elif net_architecture == "MobileNet":
        model = MobileNet(weights="imagenet", include_top=True)
    else:
        print "[ERROR] Didn't recognize net ", net_architecture
        sys.exit(-1)

    net.compile(model)
    net.save_pb(model, prefix)
    freeze.freeze(prefix)
    return

if __name__ == "__main__":
    save_imagenet("MobileNet", "/users/ahjiang/models/imagenet/mobilenet-224-imagenet")
    save_imagenet("InceptionV3", "/users/ahjiang/models/imagenet/inceptionV3-imagenet")
