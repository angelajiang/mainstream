#!/bin/bash
DATASETS="pedestrian cars flowers cats"
OPTIMIZE_METRIC=f1
LIMIT_MAX_SAMPLES=20
MAX_NUM_APPS=4
DELTA=1

for metric in f1; do
    prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/combos/$metric-4hybrid-combo-real"
    for i in $(seq 1 $DELTA $MAX_NUM_APPS); do
        echo "Num Apps:"$i
        python src/scheduler/run_scheduler_simulator.py $i \
                                              $prefix"-numapps-"$i\
                                              -m $metric \
                                              --combs \
                                              --combs-max-samples $LIMIT_MAX_SAMPLES \
                                              --datasets $DATASETS
    done
    cat $prefix*"numapps"* > $prefix"-all-"$MAX_NUM_APPS
done

# MAX_NUM_APPS=32
# DELTA=4

# for metric in f1; do
#     prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/combos/$metric-4hybrid-real"
#     for i in $(seq 4 $DELTA $MAX_NUM_APPS); do
#         echo "Num Apps:"$i
#         python src/scheduler/run_scheduler_simulator.py $i \
#                                               $prefix \
#                                               -m $metric \
#                                               --datasets $DATASETS
#     done
# done
