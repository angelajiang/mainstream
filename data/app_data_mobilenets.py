import sys

pedestrian_correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio
train_correlation_coefficient = .125 # Derived from train dataset, get_cp_ratio
correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio

def get_cp(acc, correlation_coefficient):
    delta_opt = acc
    cp = (1 - acc) + delta_opt * correlation_coefficient
    return cp

model_paths = {3:"flowers-mobilenet-80-frozen.pb",
               9:"flowers-mobilenet-80-frozen.pb",
               15:"flowers-mobilenet-80-frozen.pb",
               21:"flowers-mobilenet-80-frozen.pb",
               27:"flowers-mobilenet-80-frozen.pb",
               33:"flowers-mobilenet-80-frozen.pb",
               39:"flowers-mobilenet-80-frozen.pb",
               45:"flowers-mobilenet-80-frozen.pb",
               51:"flowers-mobilenet-80-frozen.pb",
               57:"flowers-mobilenet-80-frozen.pb",
               63:"flowers-mobilenet-80-frozen.pb",
               69:"flowers-mobilenet-80-frozen.pb",
               75:"flowers-mobilenet-80-frozen.pb",
               81:"flowers-mobilenet-80-frozen.pb",
               84:"flowers-mobilenet-80-frozen.pb"}

################# SYNTHETIC ##################

accuracy_flowers_mobilenets = {3:0.8258,
                               33:0.8258,
                               39:0.8258,
                               45:0.8258,
                               51:0.8258,
                               57:0.8203,
                               63:0.8107,
                               69:0.7860,
                               75:0.7092,
                               81:0.1468}

prob_tnr_flowers_mobilenets = {3:0.0454,
                               33:0.0454,
                               39:0.0454,
                               45:0.0454,
                               51:0.0461,
                               57:0.0474,
                               63:0.0478,
                               69:0.0520,
                               75:0.0727,
                               81:0.2040}

accuracy_cars_mobilenets = {3:0.9517,
                            33:0.9517,
                            39:0.9517,
                            45:0.9483,
                            51:0.9448,
                            57:0.9376,
                            63:0.9103,
                            69:0.9000,
                            75:0.8966,
                            81:0.4207}

prob_tnr_cars_mobilenets = {3:0.0109,
                            33:0.0109,
                            39:0.0109,
                            45:0.0109,
                            51:0.0117,
                            57:0.0153,
                            63:0.0191,
                            69:0.0214,
                            75:0.0220,
                            81:0.1222}

accuracy_cats_mobilenets = {3:0.7957,
                            33:0.7957,
                            39:0.7670,
                            45:0.7670,
                            51:0.7670,
                            57:0.7670,
                            63:0.7657,
                            69:0.7569,
                            75:0.7557,
                            81:0.2280}

prob_tnr_cats_mobilenets = {3:0.0805,
                            33:0.0805,
                            39:0.0788,
                            45:0.0788,
                            51:0.0788,
                            57:0.0788,
                            63:0.0792,
                            69:0.0813,
                            75:0.0830,
                            81:0.1856}

################# REAL ##################

accuracy_pedestrian_mobilenets = {3:0.8533,
                                  33:0.8533,
                                  39:0.8533,
                                  45:0.8533,
                                  51:0.8533,
                                  57:0.8533,
                                  63:0.8533,
                                  69:0.8533,
                                  75:0.8385,
                                  81:0.6328}

prob_tnr_pedestrian_mobilenets = {3:0.1444,
                                  33:0.1444,
                                  39:0.1444,
                                  45:0.1444,
                                  51:0.1444,
                                  57:0.1444,
                                  63:0.1444,
                                  69:0.1444,
                                  75:0.1638,
                                  81:0.4508}

accuracy_train_mobilenets = {3:0.9958,
                             33:0.9958,
                             39:0.9958,
                             45:0.9958,
                             51:0.9958,
                             57:0.9949,
                             63:0.9932,
                             69:0.9932,
                             75:0.9864,
                             81:0.568}

prob_tnr_train_mobilenets = {3:0.1563,
                             33:0.1563,
                             39:0.1563,
                             45:0.1563,
                             51:0.1563,
                             57:0.1875,
                             63:0.2000,
                             69:0.2000,
                             75:0.20000,
                             81:0.6364}

pedestrian_app = {"accuracies": accuracy_pedestrian_mobilenets,
                  "prob_tnrs" : prob_tnr_pedestrian_mobilenets,
                  "event_length_ms": 500,
                  "event_frequency": 0.3,
                  "correlation_coefficient": pedestrian_correlation_coefficient,
                  "model_path": model_paths,
                  "name": "pedestrian"}

train_app = {"accuracies": accuracy_train_mobilenets,
             "prob_tnrs" : prob_tnr_train_mobilenets,
             "event_length_ms": 500,
             "event_frequency": 0.0138,
             "correlation_coefficient": train_correlation_coefficient,
             "model_path": model_paths,
             "name": "train"}

cars_app = {"accuracies": accuracy_cars_mobilenets,
            "prob_tnrs" : prob_tnr_cars_mobilenets,
            "event_length_ms": 500,
            "event_frequency": 0.5,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cars"}

cats_app = {"accuracies": accuracy_cats_mobilenets,
            "prob_tnrs" : prob_tnr_cats_mobilenets,
            "event_length_ms": 500,
            "event_frequency": 0.3,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cats"}

flowers_app = {"accuracies": accuracy_flowers_mobilenets,
               "prob_tnrs" : prob_tnr_flowers_mobilenets,
               "event_length_ms": 500,
               "event_frequency": 0.2,
               "correlation_coefficient": correlation_coefficient,
               "model_path": model_paths,
               "name": "flowers"}

app_options = [
               pedestrian_app,
               train_app,
               cars_app,
               flowers_app,
               cats_app,
               ]

apps_by_name = {app["name"]: app for app in app_options}

mobilenets_layer_latencies = [1.0, 1.0, 1.0, 0.8685, 0.8685, 0.8685, 0.8685,
        0.8685, 0.8685, 0.4863, 0.4863, 0.4863, 0.4863, 0.4863, 0.4863, 0.6383,
        0.6383, 0.6383, 0.6383, 0.6383, 0.6383, 0.3557, 0.3557, 0.3557, 0.3557,
        0.3557, 0.3557, 0.2155, 0.2155, 0.2155, 0.2155, 0.2155, 0.2155, 0.0248,
        0.0248, 0.0248, 0.0248, 0.0248, 0.0248, 0.0378, 0.0378, 0.0378, 0.0378,
        0.0378, 0.0378, 0.0373, 0.0373, 0.0373, 0.0373, 0.0373, 0.0373, 0.0594,
        0.0594, 0.0594, 0.0594, 0.0594, 0.0594, 0.0497, 0.0497, 0.0497, 0.0497,
        0.0497, 0.0497, 0.0428, 0.0428, 0.0428, 0.0428, 0.0428, 0.0428, 0.0626,
        0.0626, 0.0626, 0.0626, 0.0626, 0.0626, 0.083, 0.083, 0.083, 0.083,
        0.083, 0.083, 0.0109, 0.0109, 0.0109]

model_desc = {"total_layers": 84,
              "channels": 1,
              "height": 299,
              "width": 299,
              "layer_latencies": mobilenets_layer_latencies,
              "frozen_layer_names": {1:"input_1",
                          3:"conv1_relu/clip_by_value",
                          9:"conv_pw_1_relu/clip_by_value",
                          15:"conv_pw_2_relu/clip_by_value",
                          21:"conv_pw_3_relu/clip_by_value",
                          27:"conv_pw_4_relu/clip_by_value",
                          33:"conv_pw_5_relu/clip_by_value",
                          39:"conv_pw_6_relu/clip_by_value",
                          45:"conv_pw_7_relu/clip_by_value",
                          51:"conv_pw_8_relu/clip_by_value",
                          57:"conv_pw_9_relu/clip_by_value",
                          63:"conv_pw_10_relu/clip_by_value",
                          69:"conv_pw_11_relu/clip_by_value",
                          75:"conv_pw_12_relu/clip_by_value",
                          81:"conv_pw_13_relu/clip_by_value",
                          84:"dense_2/Softmax:0"}}

video_desc = {"stream_fps": 15}

