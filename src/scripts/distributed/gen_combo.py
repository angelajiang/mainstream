import itertools

MAX_NUM_APPS = 10
datasets = ['cars', 'cats', 'pedestrian', 'train', 'flowers']
scheduler = 'hifi'
budget = 300

#combinations = list(itertools.chain.from_iterable(itertools.combinations(datasets, r) for r in range(5)))
#combinations = list(map(lambda x: list(x), combinations))[1:]


k = 5
combinations = itertools.combinations(datasets,k)

max_num_apps = k * MAX_NUM_APPS

print '#!/bin/bash'
for combo in combinations:
    file_suffix = reduce(lambda x,y: x + '-' + y, combo)
    datasets = reduce(lambda x,y: x + ' ' + y, combo)
    metric = 'f1'
    basenet = 'inception'

    outfile = '../mainstream-analysis/output/streamer/scheduler/distributed/%s/%s/%s-%s-%s-500' % (metric, basenet, metric, scheduler,file_suffix)
    logfile = 'log/distributed/%s-%s-%s-%s-500-mainstream-simulator.out' % (basenet,metric,scheduler,file_suffix)
    
    run_str = 'sem -j+0 python src/scheduler/run_scheduler_simulator.py %i %s -m %s --scheduler %s --budget %i --datasets %s > %s' % (max_num_apps, outfile, metric, scheduler, budget, datasets, logfile)
    print run_str

    
print 'sem --wait' 
