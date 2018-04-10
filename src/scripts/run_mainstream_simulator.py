#!/bin/bash
MAX_NUM_APPS=4
DATASET="pedestrian flowers cars cats"
SCHEDULER="hifi"
BUDGET=50
mode="f1"
for mode in mainstream nosharing maxsharing; do
    for i in $(seq 1 $MAX_NUM_APPS); do
        python src/scheduler/run_scheduler_simulator.py \
                $i ../mainstream-analysis/output/streamer/scheduler/debug/$metric-$mode \
                --mode $mode \
                --datasets $DATASET \
                --budget $BUDGET \
                --scheduler $SCHEDULER
    done
done
