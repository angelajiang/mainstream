import Pyro4
import json
import pprint as pp
import sys

if __name__ == "__main__":
    trainer = Pyro4.Proxy("PYRONAME:mainstream.trainer")
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "add":
        if len(sys.argv) != 5:
            print("add <name> <dataset_uuid> <acc_dev_percent>")
            sys.exit()
        name, dataset_uuid, acc_dev_percent = sys.argv[2:]
        acc_dev_percent = float(acc_dev_percent)
        app_uuid = trainer.add_app(name, dataset_uuid, acc_dev_percent)
        print "[client] App uuid:", app_uuid
    elif cmd == "train":
        if len(sys.argv) != 5:
            print("train <name> <image_dir> <config_file>")
            sys.exit()
        name, image_dir, config_file = sys.argv[2:]
        dataset_uuid = trainer.train_dataset(name, image_dir, config_file)
        print "[client] Dataset uuid:", dataset_uuid
    elif cmd == "ls":
        apps = trainer.list_apps()
        pp.pprint(apps)
    elif cmd == "schedule":
        schedule_json = trainer.schedule()
        print "[client]", json.dumps(schedule_json, indent=4, separators=(',', ': '))
    else:
        print("[client] Cmd should be in {add, del, train, ls, schedule}")
