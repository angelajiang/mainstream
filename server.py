import copy
import logging
import pprint as pp
import sys
import uuid
sys.path.append('training')
sys.path.append('util')
from streamer_pipelines import *
import ConfigParser
import DataSet
import FineTunerFast as ft
import Pyro4

APPS = {}
MAX_LAYERS = 314

class Helpers():

    def __init__(self):
        global APPS
        global MAX_LAYERS
        self._apps = APPS
        self._max_layers = MAX_LAYERS

    def get_accuracy_per_layer(self, uuid, image_dir, config_file, max_layers, layers_stride, patience, mock=False):
        for num_training_layers in range(0, max_layers, layers_stride):
            num_training_layers = max(1, num_training_layers)
            if mock:
                acc = .001 * num_training_layers
            else:
                print "[server] ================= Finetunning", num_training_layers, "layers ================= "
                ft_obj = ft.FineTunerFast(config_file, image_dir, "/tmp/history", patience)
                acc = ft_obj.finetune(num_training_layers)
            self._apps[uuid]["accuracy"][num_training_layers] = acc

    def get_classifier_json(self, shared_layer):
        pipeline_json = copy.deepcopy(BASIC_PIPELINE)

        base_nn = copy.deepcopy(BASIC_NN)
        base_nn["parameters"]["start_layer"] = 1
        base_nn["parameters"]["end_layer"] = shared_layer
        base_nn["processor_name"] = "base_nn"
        base_nn["inputs"]["input"] = "Transformer:output"
        pipeline_json["processors"].append(base_nn)

        for uuid, app_data in self._apps.iteritems():
            task_nn = copy.deepcopy(BASIC_NN)
            task_nn["processor_name"] = app_data["name"] + "_" + uuid + "_nn"
            task_nn["parameters"]["start_layer"] = shared_layer
            task_nn["parameters"]["end_layer"] = self._max_layers
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
        global APPS
        global MAX_LAYERS
        self._apps = APPS
        self._max_layers = MAX_LAYERS
        self.helpers = Helpers()

    def schedule(self):
        if len(self._apps) == 0:
            return {}

        all_min_layers_trained = []
        for uuid, app_data in self._apps.iteritems():
            max_acc = max(app_data["accuracy"].values())
            acc_threshold = max_acc - (app_data["acc_dev_percent"] * max_acc)
            min_layers_trained = min([layers_trained for layers_trained, accuracy in app_data["accuracy"].iteritems()  \
                                                        if accuracy >= acc_threshold])
            all_min_layers_trained.append(min_layers_trained)
        shared_layer = self._max_layers - max(all_min_layers_trained)

        return self.helpers.get_classifier_json(shared_layer)

    def list_apps(self):
        return self._apps

    def add_app(self, name, image_dir, config_file, acc_dev_percent):
        # Create an uuid to uniquely identify the app and add it to _apps datastore
        self._app_uuid = str(uuid.uuid4())[:8]
        self._apps[self._app_uuid] = {"accuracy": {}, "acc_dev_percent": acc_dev_percent, "name": name}

        # Train app with different numbers of layers frozen
        self.helpers.get_accuracy_per_layer(self._app_uuid, image_dir, config_file, self._max_layers, 50, 0, True)

        return self._app_uuid

    def del_app(self, app_id):
        if app_id in self._apps.keys():
            del self._apps[app_id]
        else:
            print "[ERROR]: App with app_id:", app_id, "is not added."

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
