#!/bin/bash

DATASETS="cars cats flowers pedestrian"
BUDGET=350
NUM_APPS=4
time python src/scheduler/run_scheduler_simulator.py \
    $NUM_APPS \
    ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-dp2 \
    --scheduler dp2 \
    --datasets $DATASETS \
    --budget $BUDGET
# MAX_NUM_APPS=10
# OPTIMIZE_METRIC=f1
# LIMIT_MAX_SAMPLES=40
# X_VOTING=0
# DATASETS=pedestrian cars flowers cats
# OUTFILE_PREFIX=../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/combos/$OPTIMIZE_METRIC-4hybrid-combo
# SEM_CMD1=sem -j+0
# SEM_CMD2=sem --wait
# if [[ ! type sem > /dev/null ]]; then
#     echo "sem (part of GNU parallel not installed)"
#     echo "Try 'pkg install parallel'"
#     echo "processing without it"
#     SEM_CMD1=
#     SEM_CMD2=
# fi
# for i in $(seq 1 $MAX_NUM_APPS); do
#     $SEM_CMD1 python src/scheduler/run_scheduler_simulator.py \
#         $i \
#         $OUTFILE_PREFIX-numapps-$i \
#         --combs \
#         --combs-max-samples $LIMIT_MAX_SAMPLES \
#         --metric $OPTIMIZE_METRIC \
#         --x-vote $X_VOTING \
#         --datasets $DATASETS
# done
# $SEM_CMD2
# cat $OUTFILE_PREFIX-numapps-*-mainstream-simulator > $OUTFILE_PREFIX-all-mainstream-simulator
