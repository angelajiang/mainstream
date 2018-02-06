#!/bin/bash
MAX_NUM_APPS=32
DELTA=4
DATASET="pedestrian flowers cars cats"
for metric in f1; do
    prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-4hybrid-real"
    for i in $(seq $DELTA $MAX_NUM_APPS); do
        python src/scheduler/run_scheduler_simulator.py $i \
                                                        $prefix \
                                                        -m $metric \
                                                        --datasets $DATASET
    done
done
