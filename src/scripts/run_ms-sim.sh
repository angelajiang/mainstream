#!/bin/bash
MAX_NUM_APPS=32
DELTA=1
for metric in f1; do
    prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-4hybrid-real"
    for dataset in train pedestrian; do
        for i in $(seq $DELTA $MAX_NUM_APPS); do
            python src/scheduler/run_scheduler_simulator.py $i \
                                                            $prefix \
                                                            -m $metric \
                                                            --datasets $dataset
        done
    done
done
