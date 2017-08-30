import Pyro4
import json
import pprint as pp
import sys

inception_chokepoints = [0, 4, 7, 10, 11, 14, 17, 18, 41, 64, 87, 101, 133, \
                         165, 197, 229, 249, 280, 311, 313]

resnet_chokepoints = [0, 2, 3, 4, 5, 17, 27, 37, 49, \
                      59, 69, 79, 91, 101, 111, \
                      121, 131, 141, 153, 163, 173, 177]

mobilenets_chokepoints = [0, 3, 9, 15, 21, 27, 33, 39, 45, 51, \
                          57, 63, 69, 75, 81, 84]

if __name__ == "__main__":

    trainer = Pyro4.Proxy("PYRONAME:mainstream.trainer")
    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) != 5:
            print("add <name> <dataset_uuid> <acc_dev_percent>")
            sys.exit()
        name, dataset_uuid, acc_dev_percent = sys.argv[2:]
        acc_dev_percent = float(acc_dev_percent)
        app_uuid = trainer.add_app(name, dataset_uuid, acc_dev_percent)
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
        apps = trainer.list_apps()
        pp.pprint(apps)

    else:
        print("[client] Cmd should be in {add, del, train, ls}")
