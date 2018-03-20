import itertools

NUM_APPS = 20
SKIP = 5
datasets = ['cars', 'cats', 'pedestrian', 'train', 'flowers']

#combinations = list(itertools.chain.from_iterable(itertools.combinations(datasets, r) for r in range(5)))
#combinations = list(map(lambda x: list(x), combinations))[1:]


k = 2
combinations = itertools.combinations(datasets,k)

print '#!/bin/bash'
for combo in combinations:
    file_suffix = reduce(lambda x,y: x + '-' + y, combo)
    datasets = reduce(lambda x,y: x + ' ' + y, combo)
    metric = 'f1'
    basenet = 'mobilenets'

    outfile = '../mainstream-analysis/output/streamer/scheduler/distributed/mass/%s/%s/%s-%s-500' % (metric, basenet, metric, file_suffix)
    logfile = 'log/distributed/mass/%s-%s-%s-500-mainstream-simulator.out' % (basenet,metric,file_suffix)
    
    run_str = 'sem -j+0 python src/scheduler/distributed_scheduling.py -d %s -m %s %i %i %s > %s' % (datasets, metric, NUM_APPS, SKIP, outfile, logfile)
    print run_str

    
print 'sem --wait' 
