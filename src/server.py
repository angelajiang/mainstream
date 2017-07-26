import copy
import logging
import pprint as pp
import persistence
import redis
import sys
import uuid
sys.path.append('src/training')
sys.path.append('src/util')
import ConfigParser
import FineTunerFast as ft
import Pyro4

if len(sys.argv) < 2:
    print "Please provide Redis port"
    sys.exit(-1)

APPS = {}
DB = redis.StrictRedis(host="localhost", port=int(sys.argv[1]), db=0)
STORE = persistence.Persistence(DB)

CHOKEPOINTS = { 0: "input_1",
                4: "conv2d_1/convolution",
                7: "conv2d_2/convolution", 
                10: "conv2d_3/convolution", 
                11: "max_pooling2d_1/MaxPool",
                14: "conv2d_4/convolution",
                17: "conv2d_5/convolution",
                18: "max_pooling2d_2/MaxPool",
                41: "mixed0/concat",
                64: "mixed1/concat",
                87: "mixed2/concat",
                101: "mixed3/concat",
                133: "mixed4/concat",
                165: "mixed5/concat",
                197: "mixed6/concat",
                229: "mixed7/concat",
                249: "mixed8/concat",
                280: "mixed9/concat",
                311: "mixed10/concat",
                313: "dense_2/Softmax:0"}

class Helpers():

    def __init__(self, store):
        self._store = store

    def get_accuracy_by_layer(self, uuid, image_dir, config_file, model_file, \
                                num_frozen_layers, log_dir):
        print "[server] ================= Freezing", num_frozen_layers, "layers ================= "
        ft_obj = ft.FineTunerFast(config_file, image_dir, log_dir + "/history", model_file)
        acc = ft_obj.finetune(num_frozen_layers)
        return acc

@Pyro4.expose
class Trainer(object):

    def __init__(self):
        global MAX_LAYERS
        global STORE
        global CHOKEPOINTS
        self._store = STORE
        self._chokepoints = CHOKEPOINTS

        self._helpers = Helpers(self._store)

    def list_apps(self):
        return self._store.get_apps_accuracies()

    def add_app(self, app_name, dataset_name, acc_dev_percent):
        app_uuid = str(uuid.uuid4())[:8]
        self._store.add_app(app_uuid, dataset_name, app_name, acc_dev_percent)
        return app_uuid

    def train_dataset(self, dataset_name, image_dir, config_file, model_dir, log_dir):
        self._store.add_dataset(dataset_name)
        layer_indices = reversed(sorted(self._chokepoints.keys()))

        acc_file = log_dir + "/" + dataset_name + "-accuracy"
        with open(acc_file, 'w+', 0) as f:
            for num_frozen_layers in layer_indices:
                model_file = model_dir + "/" +  \
                             dataset_name + "-" + \
                             str(num_frozen_layers)
                acc = self._helpers.get_accuracy_by_layer(uuid, 
                                                          image_dir, 
                                                          config_file, 
                                                          model_file, 
                                                          num_frozen_layers, 
                                                          log_dir)
                self._store.add_accuracy_by_layer(dataset_name, 
                                                  num_frozen_layers, 
                                                  acc)
        
                # Write accuracies to file
                acc_str = "%.4f" % round(acc, 4)
                line = str(num_frozen_layers) + "," + acc_str + "\n"
                f.write(line)

        return dataset_name

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
