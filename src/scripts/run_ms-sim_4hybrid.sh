#!/bin/bash
MAX_NUM_APPS=32
DELTA=4
DATASET="pedestrian flowers cars cats"
for metric in f1; do
    prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-4hybrid-real2"
    python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS \
                                                    $prefix \
                                                    -m $metric \
                                                    --datasets $DATASET
done
