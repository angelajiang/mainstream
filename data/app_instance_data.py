import sys
sys.path.append('src/scheduler/types')
import App
import Architecture

def get_app_instance(app_instance):
  if app_instance == App.AppInstance.flowers_mobilenets224:

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

    correlation_coefficient = .107

    return App.App("flowers-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_flowers_mobilenets,
                   prob_tnr_flowers_mobilenets,
                   model_paths,
                   500,
                   0.2,
                   correlation_coefficient)
