import sys
sys.path.append('src/scheduler/types')
import App
import Architecture

mobilenet_model_paths = {3:"flowers-mobilenet-80-frozen.pb",
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

def get_app_instance(app_instance):

  if app_instance == App.AppInstance.synthetic_mobilenets224:

    accuracy_train_mobilenets = {3:0,
                                 33:0,
                                 39:0,
                                 45:0,
                                 51:0,
                                 57:0,
                                 63:0,
                                 69:0,
                                 75:0,
                                 81:0}

    prob_tnr_train_mobilenets = {3:0,
                                 33:0,
                                 39:0,
                                 45:0,
                                 51:0,
                                 57:0,
                                 63:0,
                                 69:0,
                                 75:0,
                                 81:0}

    correlation_coefficient = 0
    event_length = 0
    event_frequency = 0

    return App.App("synthetic-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_train_mobilenets,
                   prob_tnr_train_mobilenets,
                   mobilenet_model_paths,
                   event_length,
                   event_frequency,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.flowers_mobilenets224:

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

    correlation_coefficient = .107

    return App.App("flowers-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_flowers_mobilenets,
                   prob_tnr_flowers_mobilenets,
                   mobilenet_model_paths,
                   500,
                   0.2,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.cars_mobilenets224:

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

    correlation_coefficient = .107

    return App.App("cars-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_cars_mobilenets,
                   prob_tnr_cars_mobilenets,
                   mobilenet_model_paths,
                   500,
                   0.5,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.cats_mobilenets224:

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

    correlation_coefficient = .107

    return App.App("cats-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_cats_mobilenets,
                   prob_tnr_cats_mobilenets,
                   mobilenet_model_paths,
                   500,
                   0.3,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.pedestrian_mobilenets224:

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

    correlation_coefficient = .107

    return App.App("pedestrian-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_pedestrian_mobilenets,
                   prob_tnr_pedestrian_mobilenets,
                   mobilenet_model_paths,
                   500,
                   0.3,
                   correlation_coefficient)

  elif app_instance == App.AppInstance.train_mobilenets224:

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

    correlation_coefficient = .125

    return App.App("train-mobilenet244",
                   Architecture.Architecture.mobilenets224,
                   accuracy_train_mobilenets,
                   prob_tnr_train_mobilenets,
                   mobilenet_model_paths,
                   500,
                   0.0138,
                   correlation_coefficient)



