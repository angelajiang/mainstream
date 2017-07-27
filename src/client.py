import Pyro4
import json
import pprint as pp
import sys

inception_chokepoints = [0, 4, 7, 10, 11, 14, 17, 18, 41, 64, 87, 101, 133, \
                         165, 197, 229, 249, 280, 311, 313]

resnet_chokepoints = [0, 2, 3, 4, 5, 15,  17, 27, 37, 49, \
                      59, 69, 79, 91, 101, 111, \
                      121, 131, 141, 153, 163, 173, 177]

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
        # TODO: check to see if we should flush the db
        if len(sys.argv) != 7:
            print("train <name> <image_dir> <config_file> <model_dir> <log_dir>")
            sys.exit()
        name, image_dir, config_file, model_dir, log_dir  = sys.argv[2:]
        dataset_uuid = trainer.train_dataset(name, image_dir, config_file, model_dir, log_dir)
        print "[client] Dataset uuid:", dataset_uuid

    elif cmd == "ls":
        apps = trainer.list_apps()
        pp.pprint(apps)

    elif cmd == "schedule":
        schedule_json = trainer.schedule()
        print "[client]", json.dumps(schedule_json, indent=4, separators=(',', ': '))

    else:
        print("[client] Cmd should be in {add, del, train, ls, schedule}")
