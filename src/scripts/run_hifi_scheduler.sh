#!/bin/bash
DATASETS="cars cats flowers pedestrian"
BUDGET=300
NUM_APPS=12
# for profiling
# python -m cProfile -s tottime \
pypy \
    src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-hifi \
    --scheduler hifi \
    --datasets $DATASETS \
    --budget $BUDGET
