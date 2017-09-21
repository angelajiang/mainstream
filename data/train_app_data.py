
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

accuracy_trains_inception = {
        0:0.736842105263,
        4:0.734335839599,
        7:0.736006683375,
        10:0.725981620718,
        11:0.726817042607,
        14:0.736842105263,
        17:0.730158730159,
        18:0.728487886383,
        41:0.757727652464,
        64:0.762740183793,
        87:0.777777777778,
        101:0.77694235589,
        133:0.745196324144,
        165:0.637426900585,
        197:0.877192982456,
        229:0.827903091061,
        249:0.760233918129,
        280:0.994987468672,
        311:0.706766917293}

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


app_options = [
               {"accuracies": accuracy_trains_inception,
                "event_length_ms": 250,
                "model_path": {
                    0:  "train-imagenet-noabcf12-0",
                    4:  "train-imagenet-noabcf12-4",
                    7:  "train-imagenet-noabcf12-7",
                    10: "train-imagenet-noabcf12-10",
                    11: "train-imagenet-noabcf12-11",
                    14: "train-imagenet-noabcf12-14",
                    17: "train-imagenet-noabcf12-17",
                    18: "train-imagenet-noabcf12-18",
                    41: "train-imagenet-noabcf12-41",
                    64: "train-imagenet-noabcf12-64",
                    87: "train-imagenet-noabcf12-87",
                    101:"train-imagenet-noabcf12-101",
                    133:"train-imagenet-noabcf12-133",
                    165:"train-imagenet-noabcf12-165",
                    197:"train-imagenet-noabcf12-197",
                    229:"train-imagenet-noabcf12-229",
                    249:"train-imagenet-noabcf12-249",
                    280:"train-imagenet-noabcf12-280",
                    311:"train-imagenet-noabcf12-313"}
                },
               {"accuracies": accuracy_flowers_inception,
                "event_length_ms": 250,
                "model_path": {
                    0:  "flowers-inception-0",
                    4:  "flowers-inception-4",
                    7:  "flowers-inception-7",
                    10: "flowers-inception-10",
                    11: "flowers-inception-11",
                    14: "flowers-inception-14",
                    17: "flowers-inception-17",
                    18: "flowers-inception-18",
                    41: "flowers-inception-41",
                    64: "flowers-inception-64",
                    87: "flowers-inception-87",
                    101:"flowers-inception-101",
                    133:"flowers-inception-133",
                    165:"flowers-inception-165",
                    197:"flowers-inception-197",
                    229:"flowers-inception-229",
                    249:"flowers-inception-249",
                    280:"flowers-inception-280",
                    311:"flowers-inception-313"}
                }
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

video_desc = {"stream_fps": 30}
