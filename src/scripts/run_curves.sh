#!/bin/bash
DATASETS="cars cats flowers pedestrian"
BUDGET=150
# NUM_APPS=12
NUM_APPS=4
# run profiling
CURVE_ADJ=(0.0 0.01 0.02 0.04 0.06 0.08 0.1 -0.01 -0.02 -0.04 -0.06 -0.08 -0.1)

#CURVE_ADJ=(0.02 0.04 0.06 0.08 0.1 -0.01 -0.02 -0.04 -0.06 -0.08 -0.1)

for i in ${CURVE_ADJ[@]}; do
    python \
        src/scheduler/run_scheduler_curves.py \
        $NUM_APPS \
        ../mainstream-analysis/output/streamer/scheduler/18Q2/schedule+${i//.} \
        --scheduler stems \
        --datasets $DATASETS \
        --budget $BUDGET \
        --curve-name pedestrian-log \
        --agg min \
        --curve-adjustment $i
done
