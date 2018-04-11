import os
import sys
sys.path.append('src/scheduler/types')
import App
import Architecture
sys.path.append('src/util')
import mpackage

mobilenet_model_paths = {0:"flowers-mobilenet-80-frozen.pb",
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
        "bus": os.path.join(curves_dir, "bus-mobilenets"),
        "cars": os.path.join(curves_dir, "cars-mobilenets"),
        "cats": os.path.join(curves_dir, "cats-mobilenets"),
        "pedestrian": os.path.join(curves_dir, "pedestrian-mobilenets"),
        "train": os.path.join(curves_dir, "trains-mobilenets"),
        }

def get_app_instance(app_instance):
  if app_instance == App.AppInstance.flowers_mobilenets224:

    correlation_coefficient = .107
    accs, acc_invs = mpackage.get_accuracy_curve(curves["flowers"])

    return App.App("flowers-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accs,
                   acc_invs,
                   mobilenet_model_paths,
                   500,
                   0.2,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.cars_mobilenets224:

    correlation_coefficient = .107
    accs, acc_invs = mpackage.get_accuracy_curve(curves["cars"])

    return App.App("cars-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accs,
                   acc_invs,
                   mobilenet_model_paths,
                   500,
                   0.5,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.cats_mobilenets224:

    correlation_coefficient = .107
    accs, acc_invs = mpackage.get_accuracy_curve(curves["cats"])

    return App.App("cats-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accs,
                   acc_invs,
                   mobilenet_model_paths,
                   500,
                   0.3,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.pedestrian_mobilenets224:

    correlation_coefficient = .107
    accs, acc_invs = mpackage.get_accuracy_curve(curves["pedestrian"])

    return App.App("pedestrian-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accs,
                   acc_invs,
                   mobilenet_model_paths,
                   500,
                   0.3,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.train_mobilenets224:

    correlation_coefficient = .125
    accs, acc_invs = mpackage.get_accuracy_curve(curves["train"])

    return App.App("train-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accs,
                   acc_invs,
                   mobilenet_model_paths,
                   500,
                   0.0138,
                   correlation_coefficient)


