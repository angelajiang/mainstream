import Pyro4
import json
import pprint as pp
import sys

if __name__ == "__main__":
    trainer = Pyro4.Proxy("PYRONAME:mainstream.trainer")
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "add":
        if len(sys.argv) != 6:
            print("add <name> <image_dir> <config_file> <acc_dev_percent>")
            sys.exit()
        name, image_dir, config_file, acc_dev_percent = sys.argv[2:]
        acc_dev_percent = float(acc_dev_percent)
        app_uuid = trainer.add_app(name, image_dir, config_file, acc_dev_percent)
        print "[client] App uuid:", app_uuid
    elif cmd == "del":
        if len(sys.argv) != 3:
            print("del <app_uuid>")
            sys.exit()
        app_uuid = sys.argv[2]
        app_uuid = trainer.del_app(app_uuid)
    elif cmd == "ls":
        apps = trainer.list_apps()
        pp.pprint(apps)
    elif cmd == "schedule":
        schedule_json = trainer.schedule()
        print "[client]", json.dumps(schedule_json, indent=4, separators=(',', ': '))
    else:
        print("[client] Cmd should be in {add, del, ls, schedule}")
