#!/bin/bash
DATASETS="cars cats flowers pedestrian"
BUDGET=200
NUM_APPS=8
# for profiling
# python -m cProfile -s tottime \
pypy \
    src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-hifi-b$BUDGET \
    --scheduler hifi \
    --datasets $DATASETS \
    --budget $BUDGET
