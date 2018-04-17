#!/bin/bash
DATASETS="cars cats flowers pedestrian"
BUDGET=150
# NUM_APPS=12
NUM_APPS=8
# run profiling
pypy -m vmprof --web \
    src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-stems \
    --scheduler stems \
    --datasets $DATASETS \
    --budget $BUDGET
