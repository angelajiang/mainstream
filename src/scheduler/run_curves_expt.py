import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data
import pprint as pp
import numpy as np
import time
from collections import defaultdict
from itertools import combinations, combinations_with_replacement

if __name__ == "__main__":

    num_apps_range = int(sys.argv[1])
    outfile = sys.argv[2]

    model_desc = app_data.model_desc
    video_desc = app_data.video_desc

    agg_funcs = {
        'mean': np.mean,
        'min': np.min,
        # TODO: normalise
    }

    def f_a(dct, fx):
        return {k: max(0., min(1., fx(v))) for k, v in dct.items()}

    curves = {
        'flowers': app_data.accuracy_flowers_inception,
        'flowers2': f_a(app_data.accuracy_flowers_inception, lambda x: x*2.),
        'flowers.5': f_a(app_data.accuracy_flowers_inception, lambda x: x*.5),
        # 'cats': app_data.accuracy_cats_inception,
        # 'trains': app_data.accuracy_trains_inception,
        # 'paris': app_data.accuracy_paris_inception,
    }
    combs = combinations_with_replacement(curves.keys(), num_apps_range)
    # combs = [('flowers', 'flowers')]

    with open(outfile, "a+", 0) as f:

        for agg_func_name, agg_func in sorted(agg_funcs.items()):
            for curves_used in combs:
                print 'agg_func:', agg_func_name
                num_apps = len(curves_used)
                print 'num_apps:', num_apps
                print 'curves:', curves_used
                # Get Schedule
                apps = []
                for i, c_used in enumerate(curves_used):
                    event_len = 250
                    print(curves[c_used])
                    # paris-95
                    apps.append({"app_id": i + 1, "accuracies": curves[c_used], "event_length_ms": event_len, "model_path": defaultdict(str)})

                # for i in range(1, num_apps + 1):
                #     index = i % len(app_data.app_options)
                #     app = dict(app_data.app_options[index])
                #     app["app_id"] = i
                #     apps.append(app)

                s = Scheduler.Scheduler(apps, video_desc,
                                        model_desc, 0, f_reduce=agg_func)

                metric = s.optimize_parameters(5000)
                rel_accs = s.get_relative_accuracies()
                agg_rel_acc = agg_func(rel_accs)
                print "FNR:", metric, ", Frozen:", s.num_frozen_list, ", FPS:", s.target_fps_list

                num_frozen_str = ",".join([str(x) for x in s.num_frozen_list])
                target_fps_str = ",".join([str(x) for x in s.target_fps_list])

                line = str(num_apps) + "," + str(round(metric, 4)) + "," + \
                    str(round(agg_rel_acc, 4)) + "," + \
                    num_frozen_str + "," + target_fps_str + "\n"
                f.write(line)
