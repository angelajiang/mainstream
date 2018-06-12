#!/bin/bash
DATASETS="cats pedestrian cars flowers"
BUDGET=100
# NUM_APPS=12
NUM_APPS=3
# run profiling
python \
    src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-eq \
    --scheduler eq \
    --datasets $DATASETS \
    --budget $BUDGET
