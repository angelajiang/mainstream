import sys
sys.path.append('src/scheduler')
import Scheduler
sys.path.append('data')
import app_data
import pprint as pp
import numpy as np
import time
import zmq
from itertools import combinations, combinations_with_replacement
import click
import os
import csv
import random

@click.command()
@click.argument('num_apps_range', type=int)
@click.argument('outfile')
@click.option('--agg', default='mean', help='agg (mean, min)')
@click.option('--curves', default='real', help='curves (real, all, all2)')
@click.option('-n', '--dry-run', is_flag=True)
@click.option('--shuffle/--no-shuffle', default=True)
def main(num_apps_range, outfile, agg, curves, dry_run, shuffle):

    kwargs = {}
    if agg == 'min':
        agg_func = np.min
    else:
        agg_func = np.average
    print agg, agg_func
    kwargs['f_reduce'] = agg_func

    if curves == 'all':
        all_apps = app_data.app_options2
    elif curves == 'all2':
        all_apps = app_data.app_options3
    else:
        all_apps = app_data.app_options
    combs = list(combinations_with_replacement(range(len(all_apps)), num_apps_range))

    if os.path.isfile(outfile):
        with open(outfile) as f:
            reader = csv.reader(row for row in f if not row.startswith('#'))
            combs_done = [line[0].replace("mean=", "").split('_') for line in reader]
            combs = [c for c in combs if map(str, c) not in combs_done]

    if dry_run:
        print len(combs)
        print combs
        return

    if shuffle:
        random.shuffle(combs)

    with open(outfile, 'a+') as f:
        writer = csv.writer(f)
        for comb in combs:
            # if len(set(comb)) == 1:
            #     continue

            # Get Schedule
            apps = []
            for i, index in enumerate(comb):
                app = dict(all_apps[index])
                app["app_id"] = i + 1
                apps.append(app)

            s = Scheduler.Scheduler(apps, app_data.video_desc,
                                    app_data.model_desc, 0, **kwargs)

            metric = s.optimize_parameters(150)
            rel_accs = s.get_relative_accuracies()
            avg_rel_acc = agg_func(rel_accs)
            comb_id = '{}={}'.format(agg, '_'.join(map(str, comb)))
            print 'Rel accs: ', rel_accs
            print 'FNRs:', s.metrics
            print "Agg: {}, Comb: {}, FNR: {}, Avg Rel Acc: {}, Frozen: {}, FPS: {}".format(agg, comb_id, metric, avg_rel_acc, s.num_frozen_list, s.target_fps_list)

            row = [
                comb_id,
                round(metric, 4),
                round(avg_rel_acc, 4),
                "_".join(map(str, s.metrics)),
                "_".join(map(str, rel_accs)),
            ]
            row += s.num_frozen_list
            row += s.target_fps_list
            writer.writerow(row)
            f.flush()

if __name__ == '__main__':
    main()