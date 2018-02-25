#!/bin/bash
NUM_APPS=32
OPTIMIZE_METRIC=f1
DATASETS="pedestrian cars flowers cats"
OUTFILE_PREFIX=../mainstream-analysis/output/streamer/scheduler/debug-atc/$OPTIMIZE_METRIC-4hybrid
python src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    $OUTFILE_PREFIX-numapps-$NUM_APPS \
    --metric $OPTIMIZE_METRIC \
    --datasets $DATASETS
