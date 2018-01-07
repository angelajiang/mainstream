import copy
import logging
import pprint as pp
import persistence
import redis
import sys
import uuid
sys.path.append('src/inference')
sys.path.append('src/scheduler')
sys.path.append('src/training')
sys.path.append('src/util')
import Schedule
import Scheduler
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

    def __init__(self, db):
        self.r = db

    def get_accuracy_by_layer(self, uuid, dataset_uuid, config_file, model_file, \
                              num_frozen_layers, log_dir, \
                              image_dir, image_test_dir):
        print "[server] ====== Freezing", num_frozen_layers, "layers ========= "
        ft_obj = ft.FineTunerFast(dataset_uuid,
                                  config_file,
                                  log_dir + "/history",
                                  model_file,
                                  image_dir,
                                  image_test_dir)
        acc = ft_obj.finetune(num_frozen_layers)
        return acc

    #have the format of "apps" in test_scheduler.py  
    #redis store everything in "String", so need to perform translation in every
    #read if we want double/int type  
    def build_apps():
        app_list = self.r.smembers("app_list")
        result = []
        for app in app_list:
            record = self.r.hgetall("app:"+app)
            dataset_uuid= record["dataset_uuid"]
            all_paths = self.r.hgetall("data:"+dataset_uuid+":path")
            model_path = {}
            for i in all_paths:
                model_path[int(i)] = all_paths[i]
            all_accs = self.r.hgetall("data:"+dataset_uuid+":acc")
            model_acc = {}
            for i in all_accs:
                model_acc[int(i)] = float(all_accs[i])
            
            record["model_path"] = model_path
            record["accuracies"] = model_acc
            record["app_id"] = app
            record["correlation"] = float(record["correlation"])
            record["event_length_ms"] = int(record["event_length_ms"])
            #record.pop('dataset_uuid')
            del record['dataset_uuid']
            result.append(record)
        print result
        return result

    def get_schedule():
        apps = self._helpers.build_apps()
        s = Scheduler.Scheduler(apps, video_desc, model_desc, 0)
        metric = s.optimize_parameters(5000)
        print "FNR:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
        schedule = s.make_streamer_schedule()
        return schedule

    def run_schedule_loop(cost_threshold, host):
        apps = self._helpers.build_apps()
        s = Scheduler.Scheduler(apps, video_desc, model_desc, 0)
        while cost_threshold > 0:
            # Get parameters
            print "[Scheduler.run] Optimizing with cost:", cost_threshold
            target_metric = s.optimize_parameters(cost_threshold)

            print "[Scheduler.run] Target metric:", target_metric

            # Get streamer schedule
            sched = s.make_streamer_schedule()

            # Deploy schedule
            fps_message = auto_deploy_schedule(sched,host)
            fpses = fps_message.split(",")
            fpses = [float(fps) for fps in fpses]

            cost_threshold = s.get_cost_threshold(sched, fpses)
            avg_rel_accs = sum(s.get_relative_accuracies()) \
                            / float(len(s.get_relative_accuracies()))
            print "[cost_threshold]: ",cost_threshold
            print "[avg_rel_accs]: ",avg_rel_accs
            observed_metric, observed_cost = s.get_observed_performance(sched, fpses)
            print "[observed_metric]: ",observed_metric
        return observed_metric, observed_cost, avg_rel_accs, s.num_frozen_list, fpses    

    def auto_deploy_schedule(schedule,host):
        ctx = zmq.Context()
        path_modified_schedule = []
        print "Deploying schedule host {}".format(host)

        for component in schedule:
            path = component["model_path"]
            print "extracting original model: "+path

            # Get frozen model
            fmodel_path = path[:-3]+"-frozen.pb"
            if not os.path.isfile(fmodel_path):
                print "generating: "+fmodel_path+ " from: "+path
                freeze(path[:-3])
            if not os.path.isfile(fmodel_path):
                print "Error: frozen model file hasn't been created: "+fmodel_path
                return 1

            # Transfer frozen model file
            print "transfering frozen model"
            start = time.time()
            a,b = zpipe(ctx)
            client_thread(ctx,b,host,fmodel_path)
            del a,b
            end = time.time()
            print "Took",end - start,"to transfer frozen model",os.path.basename(fmodel_path)
            new_component = component
            new_component["model_path"] = os.path.basename(fmodel_path)
            path_modified_schedule.append(new_component)

        # Transfer the schedule:
        print "Uploading schedule"
        print path_modified_schedule
        fpses = send_schedule(ctx, path_modified_schedule, host)
        print "going to terminate context at client"
        ctx.term()
        return fpses


@Pyro4.expose
class Trainer(object):

    def __init__(self):
        global MAX_LAYERS
        global STORE
        self.r = DB
        self._helpers = Helpers(DB)

    def list_apps():
        app_list = self.r.smembers("app_list")
        result = []
        for app in app_list:
            record = self.r.hgetall("app:"+app)
            record["app_uuid"] = app 
            result.append(record)
        print result
        return result

    # create a app:uuid and append to app_list
    def add_app(dataset_uuid, event_length, correlation):
        app_uuid = str(self.r.incr('app_uuid_counter',1))
        print app_uuid
        p = self.r.pipeline()
        p.hset("app:"+app_uuid,"dataset_uuid",dataset_uuid)
        p.hset("app:"+app_uuid,"event_length_ms",event_length)
        p.hset("app:"+app_uuid,"correlation",correlation)
        p.sadd("app_list",app_uuid)
        res = p.execute()
        print res[-1]

        return  "0" if res[-1] ==0 else app_uuid

    # delete a app:uuid and delete from the app_list
    def del_app(app_uuid):
        p = self.r.pipeline()
        p.delete("app:"+app_uuid)
        p.srem("app_list",app_uuid)
        res = p.execute()
        print res[-1]
        return "0" if res[-1] ==0 else app_uuid

    def train_dataset(self, dataset_name, config_file, model_dir, log_dir, \
                      layer_indices, image_dir, image_test_dir):

        dataset_uuid = dataset_name +"_"+ str(self.r.incr('dataset_uuid_counter',1))
        #self.r.sadd("dataset_list",dataset_uuid)
        #print "Adding dataset:"+ dataset_uuid
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
        
                # Write accuracies to file
                acc_str = "%.4f" % round(acc, 4)
                line = str(num_frozen_layers) + "," + acc_str + "\n"
                f.write(line)
        self.r.sadd("dataset_list",dataset_uuid)
        print "Adding dataset:"+ dataset_uuid
        return dataset_uuid

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(Trainer)
ns.register("mainstream.trainer", uri)

print("[server] Ready.")
daemon.requestLoop()
