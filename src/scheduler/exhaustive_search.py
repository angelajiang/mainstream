
import argparse
import scheduler_util
import Scheduler
import os
import app_data_mobilenets as app_data

VERSION = 0

def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    app_names = [app["name"] for app in app_data.app_options]
    #parser.add_argument("-n", "--num_apps", required=True, type=int)
    parser.add_argument("-o", "--outdir", required=True)
    parser.add_argument("-d", "--datasets", nargs='+', choices=app_names, required=True, help='provide one or multiple dataset names')
    parser.add_argument("-m", "--metric", default="f1")
    return parser.parse_args()


def write_cost_benefits_file(cost_benefits, outdir, filename):
    outfile = os.path.join(outdir, "configurations", filename + ".v" + str(VERSION))
    with open(outfile, "w+") as f:
        for app_id, d1 in cost_benefits.iteritems():
            for num_frozen, d2 in d1.iteritems():
                for target_fps, d3 in d2.iteritems():
                    cost = d3[0]
                    benefit = d3[1]
                    line = "{},{},{},{},{}\n".format(app_id,
                                                     num_frozen,
                                                     target_fps,
                                                     cost,
                                                     benefit)
                    f.write(line)
    return outfile


def write_model_file(layer_costs, outdir, filename):
    outfile = os.path.join(outdir, "models", filename + ".v" + str(VERSION))
    with open(outfile, "w+") as f:
        layer_costs_str = [str(c) for c in layer_costs]
        line = ",".join(layer_costs_str) + "\n"
        f.write(line)
    return outfile


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
    write_cost_benefits_file(cost_benefits, args.outdir, "test")
    write_model_file(s.model.layer_latencies, args.outdir, "test")

if __name__ == "__main__":
    main()
