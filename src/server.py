import copy
import logging
import pprint as pp
import persistence
import redis
import sys
import uuid
sys.path.append('src/training')
sys.path.append('src/util')
sys.path.append('src/inference')
import ConfigParser
import FineTunerFast as ft
import Pyro4

if len(sys.argv) < 2:
    print "Please provide Redis port"
    sys.exit(-1)

APPS = {}
DB = redis.StrictRedis(host="localhost", port=int(sys.argv[1]), db=0)
STORE = persistence.Persistence(DB)

class Helpers():

    def __init__(self, store):
        self._store = store

    def get_accuracy_by_layer(self, uuid, dataset_uuid, config_file, model_file, \
                              num_frozen_layers, log_dir, \
                              image_dir, image_test_dir):
        print "[server] ====== Freezing", num_frozen_layers, "layers ========= "
        ft_obj = ft.FineTunerFast(dataset_uuid,config_file, log_dir + "/history", model_file,
                                  image_dir, image_test_dir)
        acc = ft_obj.finetune(num_frozen_layers)
        return acc

@Pyro4.expose
class Trainer(object):

    def __init__(self):
        global MAX_LAYERS
        global STORE
        self._store = STORE
        self.r = redis.Redis(host = 'localhost',port = 6379,db = 0)
        self._helpers = Helpers(self._store)

    def list_apps(self):
        return self._store.get_apps_accuracies()

    def add_app(self, app_name, dataset_name, acc_dev_percent):
        app_uuid = str(uuid.uuid4())[:8]
        self._store.add_app(app_uuid, dataset_name, app_name, acc_dev_percent)
        return app_uuid

    def train_dataset(self, dataset_name, config_file, model_dir, log_dir, \
                      layer_indices, image_dir, image_test_dir):

        #self._store.add_dataset(dataset_name)
        
        dataset_uuid = dataset_name +"_"+ str(self.r.incr('dataset_uuid_counter',1))
        self.r.sadd("dataset_list",dataset_uuid)
        print "Adding dataset:"+ dataset_uuid
        acc_file = log_dir + "/" + dataset_name + "-accuracy"
        with open(acc_file, 'w+', 0) as f:
            for num_frozen_layers in layer_indices:
                model_file = model_dir + "/" +  \
                             dataset_name + "-" + \
                             str(num_frozen_layers)
                acc = self._helpers.get_accuracy_by_layer(uuid,
                                                          dataset_uuid, 
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
                line = str(num_frozen_layers) + "," + acc_str + "\n"
                f.write(line)
        
        return dataset_uuid

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
