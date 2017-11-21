import redis
import time
import Pyro4
import json
import pprint as pp
import sys
import Schedule
import Scheduler
import pytest
import os
import zmq
#sys.path.append('src/scheduler')
sys.path.append('../inference')
from freeze import freeze
from zmqClient import client_thread,send_schedule
from zhelpers import socket_set_hwm, zpipe

r = redis.Redis(host = 'localhost',port = 6379,db = 0)



small_video_desc = {"stream_fps": 5}
small_model_desc = {"total_layers": 41,
              "channels": 3,
              "height": 299,
              "width": 299,
              "layer_latencies": [1] * 41,
              "frozen_layer_names": {1: "input",
                                     10: "conv1",
                                     21: "conv2",
                                     30: "pool",
                                     40: "fc",
                                     41: "softmax"}}
inception_layer_latencies =  [0.179, 0.179, 0.179, 0.179, 0.3691, 0.3691,
        0.3691, 0.4197, 0.4197, 0.4197, 1.0, 0.0313, 0.0313, 0.0313, 0.5492,
        0.5492, 0.5492, 0.6753, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542,
        0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542,
        0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0542, 0.0607,
        0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607,
        0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607, 0.0607,
        0.0607, 0.0607, 0.0607, 0.0607, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621,
        0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621,
        0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621, 0.0621,
        0.0853, 0.0853, 0.0853, 0.0853, 0.0853, 0.0853, 0.0853, 0.0853, 0.0853,
        0.0853, 0.0853, 0.0853, 0.0853, 0.0853, 0.0352, 0.0352, 0.0352, 0.0352,
        0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352,
        0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352,
        0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352, 0.0352,
        0.0352, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033,
        0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033,
        0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033,
        0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0033, 0.0052, 0.0052, 0.0052,
        0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052,
        0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052,
        0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052, 0.0052,
        0.0052, 0.0052, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087,
        0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087,
        0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087,
        0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0087, 0.0091, 0.0091,
        0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091,
        0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091, 0.0091,
        0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054,
        0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054,
        0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054, 0.0054,
        0.0054, 0.0054, 0.0054, 0.0054, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051,
        0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051,
        0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051,
        0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0051, 0.0509,
        0.0509, 0.0509]

model_desc = {"total_layers": 314,
              "channels": 1,
              "height": 299,
              "width": 299,
              "layer_latencies": inception_layer_latencies,
              "frozen_layer_names": {1: "input_1",
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
                                     314: "dense_2/Softmax:0"}}

video_desc = {"stream_fps": 10}

ref_apps = [ 
        {"app_id": 1,
        "model_path": {
            0: "app1_model.pb",
            10: "app1_model.pb",
            21: "app1_model.pb",
            30: "app1_model.pb",
            40: "app1_model.pb"
        },
        "event_length_ms": 500,
        "correlation": 0,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        }]

given_sched =[{"net_id": 0,
          "app_id": -1,
          "parent_id": -1,
          "input_layer": "input",
          "output_layer": "conv1",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 8,
          "shared": True,
          "model_path": "/home/iamabcoy/Desktop/capstone/mainstream/mainstream/model/1/onetest-0.pb"
         },
         {"net_id": 3,
          "app_id": 2,
          "parent_id": 2,
          "input_layer": "pool",
          "output_layer": "softmax",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 4,
          "shared": False,
          "model_path": "/home/iamabcoy/Desktop/capstone/mainstream/mainstream/model/1/onetest-0.pb"
          }
          ]
#key: app_list
#value: app_uuid
#type: set

#key: dataset_list
#value: dataset_uuid
#type: set

#key: app:app_uuid
#value: dataset_uuid, event_length, correlation
#type: hash

#key: data:dataset_uuid:path
#value: layer:path
#type: hash

#key: data:dataset_uuid:acc
#value: layer:acc
#type: hash

#key: dataset_uuid_counter
#value: count
#type: 

#key: app_uuid_counter
#value: count
#type: 

layer_knob = [1,10,21,30,40]
def train_dataset(dataset_name,model_dir):
    #dataset_uuid = dataset_name +"_"+ str(int(time.time()))
    dataset_uuid = dataset_name +"_"+ str( r.incr('dataset_uuid_counter',1))
    print dataset_uuid
    for layer in layer_knob:
        acc = layer/100.0 #fake one
        path = model_dir + dataset_name + "_"+ str(layer) + ".pb"
        p = r.pipeline()
        p.hset("data:"+dataset_uuid+":path",layer,path)
        p.hset("data:"+dataset_uuid+":acc",layer,acc)       
        res = p.execute()
    r.sadd("dataset_list",dataset_uuid)
    return dataset_uuid

# create a app:uuid and append to app_list
def add_app(dataset_uuid, event_length,correlation):
    app_uuid = str(r.incr('app_uuid_counter',1))
    print app_uuid
    p = r.pipeline()
    p.hset("app:"+app_uuid,"dataset_uuid",dataset_uuid)
    p.hset("app:"+app_uuid,"event_length_ms",event_length)
    p.hset("app:"+app_uuid,"correlation",correlation)
    p.sadd("app_list",app_uuid)
    res = p.execute()
    print res[-1]

    return  "0" if res[-1] ==0 else app_uuid

def list_apps():
    app_list = r.smembers("app_list")
    result = []
    for app in app_list:
        record = r.hgetall("app:"+app)
        record["app_uuid"] = app 
        result.append(record)
    print result
    return result

# delete a app:uuid and delete from the app_list
def del_app(app_uuid):
    p = r.pipeline()
    p.delete("app:"+app_uuid)
    p.srem("app_list",app_uuid)
    res = p.execute()
    print res[-1]
    return "0" if res[-1] ==0 else app_uuid

#have the format of "apps" in test_scheduler.py  
#redis store everything in "String", so need to perform translation in every
#read if we want double/int type  
def build_apps():
    app_list = r.smembers("app_list")
    result = []
    for app in app_list:
        record = r.hgetall("app:"+app)
        dataset_uuid= record["dataset_uuid"]
        all_paths = r.hgetall("data:"+dataset_uuid+":path")
        model_path = {}
        for i in all_paths:
            model_path[int(i)] = all_paths[i]
        all_accs = r.hgetall("data:"+dataset_uuid+":acc")
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
    apps = build_apps()
    s = Scheduler.Scheduler(apps, video_desc, model_desc, 0)
    metric = s.optimize_parameters(5000)
    #s.num_frozen_list = [10]
    #s.target_fps_list = [2]
    #num_frozen_str = ",".join([str(x) for x in s.num_frozen_list])
    #target_fps_str = ",".join([str(x) for x in s.target_fps_list])
    print "FNR:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
    schedule = s.make_streamer_schedule()
    print schedule
    return schedule

def run_schedule_loop(cost_threshold, host):
    apps = build_apps()
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
    print "Going to deploy schedule to host ", schedule, host
    for component in schedule:
        path = component["model_path"]
        print "extracting original model: "+path
        #get frozen
        fmodel_path = path[:-3]+"-frozen.pb"
        if not os.path.isfile(fmodel_path):
            print "generating: "+fmodel_path+ " from: "+path
            freeze(path[:-3])
        if not os.path.isfile(fmodel_path):
            print "Error: frozen model file hasn't been created: "+fmodel_path
            return 1
        #transfer the model file
        print "transfering frozen model"
        a,b = zpipe(ctx)
        client_thread(ctx,b,host,fmodel_path)
        del a,b
        new_component = component
        new_component["model_path"] = os.path.basename(fmodel_path)
        path_modified_schedule.append(new_component)
    #transfer the schedule:
    print "Uploading schedule"
    print path_modified_schedule
    fpses = send_schedule(ctx, path_modified_schedule, host)
    print "going to terminate context at client"
    ctx.term()
    return fpses

if __name__ == "__main__":

    #trainer = Pyro4.Proxy("PYRONAME:mainstream.trainer")
    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) != 5:
            print("add <dataset_uuid> <event_length> <correlation>")
            # dataset_uuid from train, event length of 500, correlation of 0.16
            sys.exit()
        dataset_uuid, event_length,correlation = sys.argv[2:]
        event_length = int(event_length)
        correlation = float(correlation)
        app_uuid = add_app(dataset_uuid, event_length,correlation)
        print "[client] App uuid:", app_uuid

    elif cmd == "train":

        if len(sys.argv) == 8:
            name, config_file, model_dir, log_dir, indices, image_dir = sys.argv[2:]
            image_test_dir = None
        elif len(sys.argv) == 9:
            name, config_file, model_dir, log_dir, indices, image_dir, image_test_dir = sys.argv[2:]
        else:
            print("train <name> <config_file> <model_dir> <log_dir> <indices> <image_dir> <image_test_dir>")
            sys.exit()
        

        # Indices should be 'inceptin', 'resnet' or an int respresenting a range
        if indices == "inception":
            frozen_layer_indices = inception_chokepoints
        elif indices == "resnet":
            frozen_layer_indices = resnet_chokepoints
        elif indices == "mobilenets":
            frozen_layer_indices = mobilenets_chokepoints
        else:
            frozen_layer_indices = range(0, int(indices) + 1, 5)

        dataset_uuid = trainer.train_dataset(name,
                                             config_file,
                                             model_dir,
                                             log_dir,
                                             frozen_layer_indices,
                                             image_dir,
                                             image_test_dir)

        print "[client] Dataset uuid:", dataset_uuid

    elif cmd == "ls":
        apps = list_apps()
        pp.pprint(apps)

    elif cmd == "del":
        if len(sys.argv) != 3:
            print("del <app_uuid>")
            # provide an uuid to delete
            sys.exit()
        app_uuid = sys.argv[2]
        app_uuid = del_app(app_uuid)
        print "[client] Del App uuid:", app_uuid
    
    elif cmd == "deploy":
        if len(sys.argv) != 3:
            print("deploy <host>")
            # provide a host ip to deploy to,
            sys.exit()
        host = sys.argv[2]
        sched = get_schedule()
        auto_deploy_schedule(sched, host)

    elif cmd == "test":
        app_uuid1 = add_app("test_dataset", 500, 0.10)
        print "[client] App uuid:", app_uuid1
        app_uuid2 = add_app("test_dataset", 300, 0.15)
        print "[client] App uuid:", app_uuid2
        list_apps()
        #del_app(app_uuid1)
        #list_apps()
        #del_app(app_uuid2)
    elif cmd == "test1":
        dataset_uuid = train_dataset("test_dataset","model/1/")
    elif cmd == "test2":
        build_apps()
        print ref_apps
        #r.set(10,2)
        #print r.get(10)
    elif cmd == "test3":

        apps = build_apps()
        s = Scheduler.Scheduler(apps, video_desc, model_desc, 0)
        metric = s.optimize_parameters(5000)
        #s.num_frozen_list = [10]
        #s.target_fps_list = [2]
        #num_frozen_str = ",".join([str(x) for x in s.num_frozen_list])
        #target_fps_str = ",".join([str(x) for x in s.target_fps_list])
        print "FNR:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
        schedule = s.make_streamer_schedule()
        print schedule
    elif cmd == "test31":
        s = Scheduler.Scheduler(ref_apps, small_video_desc, small_model_desc, 0)
        metric = s.optimize_parameters(5000)
        print "FNR:", metric, ", Frozen:", s.num_frozen_list, ", FPS:",  s.target_fps_list
        schedule = s.make_streamer_schedule()
        print schedule

    elif cmd == "test4":
        auto_deploy_schedule(given_sched,"istc-vcs.pc.cc.cmu.edu")

    elif cmd == "test5":
        run_schedule_loop(500,"istc-vcs.pc.cc.cmu.edu")

    else:
        print("[client] Cmd should be in {add, del, train, ls}")
