
def flip(acc_map, total_layers):
    new_acc_map = {}
    for layer, acc in acc_map.iteritems():
        key = total_layers - layer
        new_acc_map[key] = acc
    return new_acc_map

# TODO: Get values from redis
accuracy_flowers_inception = {#0:0.882,
                              #4:0.882,
                              #7:0.8834,
                              #10:0.882,
                              #11:0.8807,
                              14:0.8834,
                              #17:0.8807,
                              18:0.882,
                              #41:0.8807,
                              #64:0.8807,
                              87:0.8807,
                              #101:0.8765,
                              133:0.8779,
                              165:0.8765,
                              197:0.8697,
                              #229:0.8615,
                              249:0.8477,
                              280:0.7284,
                              311:0.2606}

accuracy_cats_inception = {#0:0.7684,
                           #4:0.7720,
                           #7:0.7720,
                           #10:0.7708,
                           #11:0.7809,
                           #14:0.7858,
                           #17:0.7834,
                           18:0.7996,
                           41:0.7984,
                           #64:0.7884,
                           #87:0.7821,
                           #101:0.7821,
                           133:0.7922,
                           #165:0.7821,
                           197:0.7834,
                           229:0.7809,
                           249:0.7632,
                           280:0.7418,
                           311:0.4836}

accuracy_trains_inception = flip({#314:0.9855,
                            #310:0.9855,
                            #307:0.9831,
                            #304:0.9879,
                            #303:0.9879,
                            #300:0.9879,
                            #297:0.9831,
                            #296:0.9831,
                            #273:0.9831,
                            #250:0.9831,
                            #227:0.9831,
                            #213:0.9831,
                            #181:0.9831,
                            #149:0.9855,
                            117:0.9952,
                            85:0.9952,
                            65:0.9952,
                            34:0.9831,
                            3:0.9080
                            #1:0.6610
                            }, 314)

accuracy_paris_inception = {#0:0.8922,
                            #4:0.8922,
                            #7:0.8892,
                            #10:0.8922,
                            #11:0.8922,
                            #14:0.8922,
                            #17:0.8922,
                            #18:0.8922,
                            #41:0.8922,
                            #64:0.8922,
                            #87:0.8922,
                            #101:0.8922,
                            133:0.8952,
                            165:0.8832,
                            197:0.8772,
                            229:0.8743,
                            249:0.8653,
                            280:0.7335,
                            311:0.2545}

inception_layer_latencies =  [0.0888, 0.0888, 0.0888, 0.0888, 0.1373, 0.1373,
        0.1373, 0.2449, 0.2449, 0.2449, 0.2613, 0.2565, 0.2565, 0.2565, 0.4655,
        0.4655, 0.4655, 0.3402, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201,
        0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201,
        0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.6201, 0.5133,
        0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133,
        0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133, 0.5133,
        0.5133, 0.5133, 0.5133, 0.5133, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973,
        0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973,
        0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973, 0.7973,
        0.6614, 0.6614, 0.6614, 0.6614, 0.6614, 0.6614, 0.6614, 0.6614, 0.6614,
        0.6614, 0.6614, 0.6614, 0.6614, 0.6614, 0.9368, 0.9368, 0.9368, 0.9368,
        0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368,
        0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368,
        0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368, 0.9368,
        0.9368, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744,
        0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744,
        0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744,
        0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.6744, 0.9576, 0.9576, 0.9576,
        0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576,
        0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576,
        0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576, 0.9576,
        0.9576, 0.9576, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091,
        0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091,
        0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091,
        0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.7091, 0.9803, 0.9803,
        0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803,
        0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803, 0.9803,
        0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298,
        0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298,
        0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298, 0.7298,
        0.7298, 0.7298, 0.7298, 0.7298, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.7424, 0.7424, 0.7242]


app_options = [
               #{"accuracies": accuracy_trains_inception,
               # "model_path": "/home/ahjiang/models/trains-40-0.0001-310-frozen.pb"},
               {"accuracies": accuracy_flowers_inception,
                "event_length_ms": 500,
                "model_path": "/home/ahjiang/models/flowers-310-frozen.pb"}
               #{"accuracies": accuracy_cats_inception,
               # "event_length_ms": 250,
               # "model_path": "/home/ahjiang/models/flowers-310-frozen.pb"}
               {"accuracies": accuracy_cats_inception,
                "event_length_ms": 250,
                "model_path": "/home/ahjiang/models/flowers-310-frozen.pb"}
               #{"accuracies": accuracy_paris_inception,
               # "model_path": "/home/ahjiang/models/paris-95-frozen.pb"}
               ]

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

video_desc = {"stream_fps": 14}
