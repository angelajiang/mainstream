#!/bin/bash
MAX_NUM_APPS=32
DATASET="pedestrian flowers cars cats"
for metric in f1; do
    for i in $(seq 1 $MAX_NUM_APPS); do
        python src/scheduler/run_scheduler_simulator.py $i ../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-4hybrid-real -m $metric --datasets $DATASET
    done
done
