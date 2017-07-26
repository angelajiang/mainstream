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
MAX_LAYERS = 314
DB = redis.StrictRedis(host="localhost", port=int(sys.argv[1]), db=0)
STORE = persistence.Persistence(DB)

# TODO: Change keys to num_frozen. e.g.) 0:input_1, 313:softmax
CHOKEPOINTS = { 314: "input_1",
                310: "conv2d_1/convolution",
                307: "conv2d_2/convolution", 
                304: "conv2d_3/convolution", 
                303: "max_pooling2d_1/MaxPool",
                300: "conv2d_4/convolution",
                297: "conv2d_5/convolution",
                296: "max_pooling2d_2/MaxPool",
                273: "mixed0/concat",
                250: "mixed1/concat",
                227: "mixed2/concat",
                213: "mixed3/concat",
                181: "mixed4/concat",
                149: "mixed5/concat",
                117: "mixed6/concat",
                85: "mixed7/concat",
                65: "mixed8/concat",
                34: "mixed9/concat",
                3: "mixed10/concat",
                1: "dense_2/Softmax:0"}

class Helpers():

    def __init__(self, store):
        self._store = store

    def get_accuracy_by_layer(self, uuid, image_dir, config_file, model_file, \
                                num_training_layers, log_dir, mock=False):
        if mock:
            acc = .001 * num_training_layers
        else:
            print "[server] ================= Finetunning", num_training_layers, "layers ================= "
            ft_obj = ft.FineTunerFast(config_file, image_dir, log_dir + "/history", model_file)
            acc = ft_obj.finetune(num_training_layers)
        return acc

    def get_classifier_json(self, shared_layer, max_layers):
        pipeline_json = copy.deepcopy(BASIC_PIPELINE)

        base_nn = copy.deepcopy(BASIC_NN)
        base_nn["parameters"]["start_layer"] = 1
        base_nn["parameters"]["end_layer"] = shared_layer
        base_nn["processor_name"] = "base_nn"
        base_nn["inputs"]["input"] = "Transformer:output"
        pipeline_json["processors"].append(base_nn)

        app_uuids = self._store.get_app_uuids()
        for uuid in app_uuids:
            app_data = self._store.get_app_data(uuid)
            task_nn = copy.deepcopy(BASIC_NN)
            task_nn["processor_name"] = app_data["name"] + "_" + uuid + "_nn"
            task_nn["parameters"]["start_layer"] = shared_layer
            task_nn["parameters"]["end_layer"] = max_layers
            task_nn["inputs"]["input"] = base_nn["processor_name"] + ":output"
            pipeline_json["processors"].append(task_nn)
            task_classifier = copy.deepcopy(BASIC_CLASSIFIER)
            task_classifier["processor_name"] = app_data["name"] + "_" + uuid + "_classifier"
            task_classifier["inputs"]["input"] = task_nn["processor_name"] + ":output"
            pipeline_json["processors"].append(task_classifier)

        return pipeline_json

@Pyro4.expose
class Trainer(object):

    def __init__(self):
        global MAX_LAYERS
        global STORE
        global CHOKEPOINTS
        self._max_layers = MAX_LAYERS
        self._store = STORE
        self._chokepoints = CHOKEPOINTS

        self._helpers = Helpers(self._store)

    def schedule(self):
        # REDIS
        app_uuids = self._store.get_app_uuids()
        if len(app_uuids) == 0:
            return {}

        all_min_layers_trained = []
        app_accuracies = self._store.get_apps_accuracies()
        for uuid in app_uuids:
            max_acc_layer = max(app_accuracies[uuid].keys())
            max_acc = app_accuracies[uuid][max_acc_layer]
            acc_dev_percent = self._store.get_acc_dev_by_app_uuid(uuid)
            acc_threshold = max_acc - (acc_dev_percent * max_acc)
            for app_uuid, accuracies in app_accuracies.iteritems():
                min_layers_trained = min([layers_trained for layers_trained, accuracy in accuracies.iteritems()  \
                                                            if accuracy >= acc_threshold])
            all_min_layers_trained.append(min_layers_trained)
        shared_layer = self._max_layers - max(all_min_layers_trained)
        return self._helpers.get_classifier_json(shared_layer, self._max_layers)

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
            for num_training_layers in layer_indices:
                num_frozen_layers = self._max_layers - num_training_layers
                model_file = model_dir + "/" + 
                             dataset_name + "-" +
                             str(num_frozen_layers)

                model_file = self._helpers.get_model_file(model_dir, 
                                                          dataset_name, 
                                                          num_frozen_layers)
                acc = self._helpers.get_accuracy_by_layer(uuid, 
                                                          image_dir, 
                                                          config_file, 
                                                          model_file, 
                                                          num_frozen_layers, 
                                                          log_dir,
                                                          False)
                self._store.add_accuracy_by_layer(dataset_name, 
                                                  num_frozen_layers, 
                                                  acc)
        
                # Write accuracies to file
                layer_name = self._chokepoints[num_training_layers]
                acc_str = "%.4f" % round(acc, 4)
                line = str(num_frozen_layers) + "," + layer_name + "," + acc_str + "\n"
                f.write(line)

        return dataset_name

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
