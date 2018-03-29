import copy
import logging
import pprint as pp
import persistence
import redis
import sys
import uuid
sys.path.append('src/training')
sys.path.append('src/util')
import configparser
import FineTunerFast as ft
import Pyro4


@Pyro4.expose
class Trainer(object):

    def get_accuracy_by_layer(self, uuid, config_file, model_file, \
                              num_frozen_layers, log_dir, \
                              image_dir, image_test_dir):
        ft_obj = ft.FineTunerFast(config_file, log_dir + "/history", model_file,
                                  image_dir, image_test_dir)
        acc, fcc = ft_obj.finetune(num_frozen_layers)
        return acc, fcc

    def list_apps(self):
        return self._store.get_apps_accuracies()

    def add_app(self, app_name, dataset_name, acc_dev_percent):
        app_uuid = str(uuid.uuid4())[:8]
        self._store.add_app(app_uuid, dataset_name, app_name, acc_dev_percent)
        return app_uuid

    def train_dataset(self, dataset_name, config_file, model_dir, log_dir, \
                      layer_indices, image_dir, image_test_dir):

        #self._store.add_dataset(dataset_name)

        acc_file = log_dir + "/" + dataset_name + "-accuracy"
        with open(acc_file, 'w+') as f:
            for num_frozen_layers in layer_indices:
                model_file = model_dir + "/" +  \
                             dataset_name + "-" + \
                             str(num_frozen_layers)
                acc, fcc = self.get_accuracy_by_layer(uuid,
                                                               config_file,
                                                               model_file,
                                                               num_frozen_layers,
                                                               log_dir,
                                                               image_dir,
                                                               image_test_dir)
                '''
                self._store.add_accuracy_by_layer(dataset_name, 
                                                  num_frozen_layers, 
                                                  acc)
                '''

                # Write accuracies to file
                acc_str = "%.4f" % round(acc, 4)
                fcc_str = "%.4f" % round(fcc, 4)
                line = str(num_frozen_layers) + "," + acc_str + "," + fcc_str + "\n"
                f.write(line)

        return dataset_name

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
