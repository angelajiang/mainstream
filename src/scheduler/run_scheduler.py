import sys
sys.path.append('src/scheduler')
import scheduler
import pprint as pp
import zmq

def flip(acc_map, total_layers):
    new_acc_map = {}
    for layer, acc in acc_map.iteritems():
        key = total_layers - layer
        new_acc_map[key] = acc
    return new_acc_map

# TODO: Get values from redis
accuracy_flowers_inception = flip({314:0.8121,
                              310:0.8121,
                              307:0.8203,
                              304:0.8203,
                              303:0.8162,
                              300:0.8189,
                              297:0.8217,
                              296:0.8189,
                              273:0.8162,
                              250:0.8148,
                              227:0.8107,
                              213:0.8217,
                              181:0.8203,
                              149:0.8121,
                              117:0.8176,
                              85:0.8189,
                              65:0.8669,
                              34:0.8477,
                              3:0.7380,
                              1:0.2346}, 314)

accuracy_trains_inception = flip({314:0.9855,
                            310:0.9855,
                            307:0.9831,
                            304:0.9879,
                            303:0.9879,
                            300:0.9879,
                            297:0.9831,
                            296:0.9831,
                            273:0.9831,
                            250:0.9831,
                            227:0.9831,
                            213:0.9831,
                            181:0.9831,
                            149:0.9855,
                            117:0.9952,
                            85:0.9952,
                            65:0.9952,
                            34:0.9831,
                            3:0.9080,
                            1:0.6610}, 314)

accuracy_paris_inception = flip({314:0.8533,
                            310:0.8593,
                            307:0.8533,
                            304:0.8533,
                            303:0.8533,
                            300:0.8503,
                            297:0.8533,
                            296:0.8533,
                            273:0.8503,
                            250:0.8593,
                            227:0.8353,
                            213:0.8263,
                            181:0.8383,
                            149:0.8353,
                            117:0.8263,
                            85:0.8204,
                            65:0.8713,
                            34:0.8533,
                            3:0.7246,
                            1:0.2395}, 314)

app_options = [{"accuracies": accuracy_flowers_inception,
                "model_path": "/home/ahjiang/models/flowers-40-0.0001-310-frozen.pb"},
               {"accuracies": accuracy_trains_inception,
                "model_path": "/home/ahjiang/models/trains-40-0.0001-310-frozen.pb"},
               {"accuracies": accuracy_paris_inception,
                "model_path": "/home/ahjiang/models/trains-resized-40-0.0001-310-frozen.pb"}]

model_desc = {"total_layers": 314,
              "channels": 1,
              "height": 299,
              "width": 299,
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

if __name__ == "__main__":

    # Get Schedule
    num_apps = int(sys.argv[1])
    threshold = float(sys.argv[2])

    apps = []
    for i in range(num_apps):
        index = i % len(app_options)
        app = app_options[index]
        apps.append(app)

    sched = scheduler.schedule(apps, threshold, model_desc)

    # Deploy schedule
    context = zmq.Context()

    print "Connecting to Streamer server..."
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_json(sched)

    # Get the reply.
    message = socket.recv()
    print "Received reply ", message

