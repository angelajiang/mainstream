
import argparse
import scheduler_util
import Scheduler
import app_data_mobilenets as app_data

def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    #parser.add_argument("-n", "--num_apps", required=True, type=int)
    parser.add_argument("-o", "--outfile", required=True)
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide one or multiple dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    return parser.parse_args()

def main():
    args = get_args()
    min_metric = args.metric
    app_datasets = [app_data.apps_by_name[app_name] for app_name in args.datasets]
    all_apps = []
    for i, app in enumerate(app_datasets):
        app["app_id"] = i
        all_apps.append(app)
    s = Scheduler.Scheduler(min_metric, all_apps, app_data.video_desc,
                            app_data.model_desc, 0)
    cost_benefits = s.get_cost_benefits()

if __name__ == "__main__":
    main()
