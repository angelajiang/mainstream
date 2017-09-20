
def flip(acc_map, total_layers):
    new_acc_map = {}
    for layer, acc in acc_map.iteritems():
        key = total_layers - layer
        new_acc_map[key] = acc
    return new_acc_map


def make_monotonic(acc_map, del_dup=True):
    acc = reversed(sorted(acc_map.items()))
    best_so_far = -1.
    acc_map_ret = dict(acc_map)
    for k, v in acc:
        if v >= best_so_far:
            best_so_far = v
        else:
            if del_dup:
                del acc_map_ret[k]
            else:
                acc_map_ret[k] = best_so_far
    return acc_map_ret


def combine_accs(apps):
    def flatten(lst):
        return [l for sl in lst for l in sl]
    layers = set(flatten([make_monotonic(a["accuracies"]).keys() for a in apps]))
    for app in apps:
        orig = make_monotonic(app["accuracies"], del_dup=False)
        app["accuracies"] = {l: orig[l] for l in layers}
    return apps


# TODO: Get values from redis
accuracy_flowers_inception = {0:0.882,
                              4:0.882,
                              7:0.8834,
                              10:0.882,
                              11:0.8807,
                              14:0.8834,
                              17:0.8807,
                              18:0.882,
                              41:0.8807,
                              64:0.8807,
                              87:0.8807,
                              101:0.8765,
                              133:0.8779,
                              165:0.8765,
                              197:0.8697,
                              229:0.8615,
                              249:0.8477,
                              280:0.7284,
                              311:0.2606}

accuracy_cats_inception = {0:0.7684,
                           4:0.7720,
                           7:0.7720,
                           10:0.7708,
                           11:0.7809,
                           14:0.7858,
                           17:0.7834,
                           18:0.7996,
                           41:0.7984,
                           64:0.7884,
                           87:0.7821,
                           101:0.7821,
                           133:0.7922,
                           165:0.7821,
                           197:0.7834,
                           229:0.7809,
                           249:0.7632,
                           280:0.7418,
                           311:0.4836}

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
                            3:0.9080
                            #1:0.6610
                            }, 314)

accuracy_paris_inception = {0:0.8922,
                            4:0.8922,
                            7:0.8892,
                            10:0.8922,
                            11:0.8922,
                            14:0.8922,
                            17:0.8922,
                            18:0.8922,
                            41:0.8922,
                            64:0.8922,
                            87:0.8922,
                            101:0.8922,
                            133:0.8952,
                            165:0.8832,
                            197:0.8772,
                            229:0.8743,
                            249:0.8653,
                            280:0.7335,
                            311:0.2545}


accuracy_artificial_linear = {0: 1.0,
 4: 0.9936305732484076,
 7: 0.9888535031847134,
 10: 0.9840764331210191,
 11: 0.9824840764331211,
 14: 0.9777070063694268,
 17: 0.9729299363057324,
 18: 0.9713375796178344,
 41: 0.9347133757961783,
 64: 0.8980891719745223,
 87: 0.8614649681528662,
 101: 0.839171974522293,
 133: 0.7882165605095541,
 165: 0.7372611464968153,
 197: 0.6863057324840764,
 229: 0.6353503184713376,
 249: 0.6035031847133758,
 280: 0.554140127388535,
 311: 0.5047770700636942}


accuracy_artificial_log = {0: 0.948917437623401,
 4: 0.9476353687804948,
 7: 0.9466629137912953,
 10: 0.9456809091731978,
 11: 0.9453514195835125,
 14: 0.9443563864981956,
 17: 0.9433513529128456,
 18: 0.9430140844649816,
 41: 0.9349253185510715,
 64: 0.9261242308188002,
 87: 0.9164731407807158,
 101: 0.9101073556035181,
 133: 0.8938278421591581,
 165: 0.8743727696271215,
 197: 0.8501955325123511,
 229: 0.8182432646816072,
 249: 0.7914168660221392,
 280: 0.7266141914941917,
 311: 0.48383936789938653}

accuracy_artificial_inflection = {0: 0.9403981232249272,
 4: 0.9256740937090324,
 7: 0.9127547960014948,
 10: 0.8981272858281896,
 11: 0.8928630457799425,
 14: 0.8759031652053395,
 17: 0.8572341339226256,
 18: 0.8506494408751837,
 41: 0.6758568834488784,
 64: 0.555679791618946,
 87: 0.5139724469671008,
 101: 0.5056104547324075,
 133: 0.4987945881346533,
 165: 0.4853080961003995,
 197: 0.4051837697448209,
 229: 0.1787797556285336,
 249: 0.06735942871014962,
 280: 0.010578623740894147,
 311: 0.0014958593820696806}


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


app_options = combine_accs([
               {"accuracies": accuracy_flowers_inception,
                "event_length_ms": 250,
                "model_path": {
                    0:  "flowers-310-frozen.pb",
                    4:  "flowers-310-frozen.pb",
                    7:  "flowers-310-frozen.pb",
                    10: "flowers-310-frozen.pb",
                    11: "flowers-310-frozen.pb",
                    14: "flowers-310-frozen.pb",
                    17: "flowers-310-frozen.pb",
                    18: "flowers-310-frozen.pb",
                    41: "flowers-310-frozen.pb",
                    64: "flowers-310-frozen.pb",
                    87: "flowers-310-frozen.pb",
                    101:"flowers-310-frozen.pb",
                    133:"flowers-310-frozen.pb",
                    165:"flowers-310-frozen.pb",
                    197:"flowers-310-frozen.pb",
                    229:"flowers-310-frozen.pb",
                    249:"flowers-310-frozen.pb",
                    280:"flowers-310-frozen.pb",
                    311:"flowers-310-frozen.pb"}
                },
               {"accuracies": accuracy_cats_inception,
               "event_length_ms": 250,
               "model_path": "flowers-310-frozen.pb"},
               {"accuracies": accuracy_paris_inception,
               "model_path": "paris-95-frozen.pb",
               "event_length_ms": 250},
               ])

app_options2 = combine_accs([
              {"accuracies": accuracy_artificial_linear,
              "event_length_ms": 250,
              "model_path": "flowers-310-frozen.pb"},
              {"accuracies": accuracy_artificial_log,
              "event_length_ms": 250,
              "model_path": "flowers-310-frozen.pb"},
               {"accuracies": accuracy_flowers_inception,
                "event_length_ms": 250,
                "model_path": {
                    0:  "flowers-310-frozen.pb",
                    4:  "flowers-310-frozen.pb",
                    7:  "flowers-310-frozen.pb",
                    10: "flowers-310-frozen.pb",
                    11: "flowers-310-frozen.pb",
                    14: "flowers-310-frozen.pb",
                    17: "flowers-310-frozen.pb",
                    18: "flowers-310-frozen.pb",
                    41: "flowers-310-frozen.pb",
                    64: "flowers-310-frozen.pb",
                    87: "flowers-310-frozen.pb",
                    101:"flowers-310-frozen.pb",
                    133:"flowers-310-frozen.pb",
                    165:"flowers-310-frozen.pb",
                    197:"flowers-310-frozen.pb",
                    229:"flowers-310-frozen.pb",
                    249:"flowers-310-frozen.pb",
                    280:"flowers-310-frozen.pb",
                    311:"flowers-310-frozen.pb"}
                },
               {"accuracies": accuracy_cats_inception,
               "event_length_ms": 250,
               "model_path": "flowers-310-frozen.pb"},
               {"accuracies": accuracy_paris_inception,
               "model_path": "paris-95-frozen.pb",
               "event_length_ms": 250},
               ])

app_options3 = combine_accs([
              {"accuracies": accuracy_artificial_linear,
              "event_length_ms": 250,
              "model_path": "flowers-310-frozen.pb"},
              {"accuracies": accuracy_artificial_log,
              "event_length_ms": 250,
              "model_path": "flowers-310-frozen.pb"},
               {"accuracies": accuracy_flowers_inception,
                "event_length_ms": 250,
                "model_path": {
                    0:  "flowers-310-frozen.pb",
                    4:  "flowers-310-frozen.pb",
                    7:  "flowers-310-frozen.pb",
                    10: "flowers-310-frozen.pb",
                    11: "flowers-310-frozen.pb",
                    14: "flowers-310-frozen.pb",
                    17: "flowers-310-frozen.pb",
                    18: "flowers-310-frozen.pb",
                    41: "flowers-310-frozen.pb",
                    64: "flowers-310-frozen.pb",
                    87: "flowers-310-frozen.pb",
                    101:"flowers-310-frozen.pb",
                    133:"flowers-310-frozen.pb",
                    165:"flowers-310-frozen.pb",
                    197:"flowers-310-frozen.pb",
                    229:"flowers-310-frozen.pb",
                    249:"flowers-310-frozen.pb",
                    280:"flowers-310-frozen.pb",
                    311:"flowers-310-frozen.pb"}
                },
               {"accuracies": accuracy_cats_inception,
               "event_length_ms": 250,
               "model_path": "flowers-310-frozen.pb"},
               {"accuracies": accuracy_paris_inception,
               "model_path": "paris-95-frozen.pb",
               "event_length_ms": 250},
               {"accuracies": accuracy_artificial_inflection,
               "event_length_ms": 250,
               "model_path": "flowers-310-frozen.pb"}
             ])


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
