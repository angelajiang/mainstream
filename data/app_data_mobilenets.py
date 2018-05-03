import os
import sys
sys.path.append('src/util')
import mpackage

pedestrian_correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio
train_correlation_coefficient = .125 # Derived from train dataset, get_cp_ratio
correlation_coefficient = .107 # Derived from pedestrian dataset, get_cp_ratio

def get_cp(acc, correlation_coefficient):
    delta_opt = acc
    cp = (1 - acc) + delta_opt * correlation_coefficient
    return cp

model_paths = {0:"flowers-mobilenet-80-frozen.pb",
               3:"flowers-mobilenet-80-frozen.pb",
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

# Accuracy curve files
curves_dir = "data/mpackages"
curves = {
        "flowers": os.path.join(curves_dir, "flowers-mobilenets"),
        "cars": os.path.join(curves_dir, "cars-mobilenets"),
        "cats": os.path.join(curves_dir, "cats-mobilenets"),
        "pedestrian": os.path.join(curves_dir, "pedestrian-mobilenets"),
        "train": os.path.join(curves_dir, "trains-mobilenets"),
        "bus": os.path.join(curves_dir, "bus-mobilenets"),
        "redcar": os.path.join(curves_dir, "redcar-mobilenets"),
        "scramble": os.path.join(curves_dir, "scramble-mobilenets"),
        "schoolbus": os.path.join(curves_dir, "schoolbus-mobilenets"),
        }

pedestrian_app = {"accuracies": mpackage.get_accuracy_curve(curves["pedestrian"])[0],
                  "prob_tnrs" : mpackage.get_accuracy_curve(curves["pedestrian"])[1],
                  "event_length_ms": 500,
                  "event_frequency": 0.3,
                  "correlation_coefficient": pedestrian_correlation_coefficient,
                  "model_path": model_paths,
                  "name": "pedestrian"}

train_app = {"accuracies": mpackage.get_accuracy_curve(curves["train"])[0],
             "prob_tnrs" : mpackage.get_accuracy_curve(curves["train"])[1],
             "event_length_ms": 500,
             "event_frequency": 0.0138,
             "correlation_coefficient": train_correlation_coefficient,
             "model_path": model_paths,
             "name": "train"}

cars_app = {"accuracies": mpackage.get_accuracy_curve(curves["cars"])[0],
            "prob_tnrs" : mpackage.get_accuracy_curve(curves["cars"])[1],
            "event_length_ms": 500,
            "event_frequency": 0.5,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cars"}

cats_app = {"accuracies": mpackage.get_accuracy_curve(curves["cats"])[0],
            "prob_tnrs" : mpackage.get_accuracy_curve(curves["cats"])[1],
            "event_length_ms": 500,
            "event_frequency": 0.3,
            "correlation_coefficient": correlation_coefficient,
            "model_path": model_paths,
            "name": "cats"}

flowers_app = {"accuracies": mpackage.get_accuracy_curve(curves["flowers"])[0],
               "prob_tnrs" : mpackage.get_accuracy_curve(curves["flowers"])[1],
               "event_length_ms": 500,
               "event_frequency": 0.2,
               "correlation_coefficient": correlation_coefficient,
               "model_path": model_paths,
               "name": "flowers"}

bus_app = {"accuracies": mpackage.get_accuracy_curve(curves["bus"])[0],
           "prob_tnrs" : mpackage.get_accuracy_curve(curves["bus"])[1],
           "event_length_ms": 500,
           "event_frequency": 0.2,
           "correlation_coefficient": correlation_coefficient,
           "model_path": model_paths,
           "name": "bus"}

schoolbus_app = {"accuracies": mpackage.get_accuracy_curve(curves["schoolbus"])[0],
                 "prob_tnrs" : mpackage.get_accuracy_curve(curves["schoolbus"])[1],
                 "event_length_ms": 500,
                 "event_frequency": 0.2,
                 "correlation_coefficient": correlation_coefficient,
                 "model_path": model_paths,
                 "name": "schoolbus"}

redcar_app = {"accuracies": mpackage.get_accuracy_curve(curves["redcar"])[0],
              "prob_tnrs" : mpackage.get_accuracy_curve(curves["redcar"])[1],
              "event_length_ms": 500,
              "event_frequency": 0.2,
              "correlation_coefficient": correlation_coefficient,
              "model_path": model_paths,
              "name": "redcar"}

scramble_app = {"accuracies": mpackage.get_accuracy_curve(curves["scramble"])[0],
                "prob_tnrs" : mpackage.get_accuracy_curve(curves["scramble"])[1],
                "event_length_ms": 500,
                "event_frequency": 0.2,
                "correlation_coefficient": correlation_coefficient,
                "model_path": model_paths,
                "name": "scramble"}

app_options = [
               pedestrian_app,
               train_app,
               cars_app,
               flowers_app,
               cats_app,
               bus_app,
               schoolbus_app,
               scramble_app,
               redcar_app
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
        0.083, 0.083, 0.0109, 0.0109, 0.0109, 0.0109]

model_desc = {"total_layers": 85,
              "channels": 1,
              "height": 224,
              "width": 224,
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
                                     84:"dense1/Relu",
                                     85:"dense_2/Softmax:0"}}

video_desc = {"stream_fps": 15}

