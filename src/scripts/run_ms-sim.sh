#!/bin/bash
MAX_NUM_APPS=32
DELTA=1
for metric in f1; do
    for dataset in train pedestrian; do
        prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-$dataset-500-real"
        python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS \
                                                        $prefix \
                                                        -m $metric \
                                                        --datasets $dataset
    done
done
