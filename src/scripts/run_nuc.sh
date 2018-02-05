#!/bin/bash
MAX_NUM_APPS=4
OPTIMIZE_METRIC=f1
LIMIT_MAX_SAMPLES=100
DATASETS="pedestrian cars flowers cats"
#DATASET=train


for metric in f1; do
    prefix="../mainstream-analysis/output/streamer/scheduler/atc/$metric/combos/$metric-4hybrid-combo"
    for i in $(seq 1 $MAX_NUM_APPS); do
        python src/scheduler/run_scheduler.py $MAX_NUM_APPS \
                                              $prefix"-numapps-"$i\
                                              -m $metric \
                                              --versions nosharing maxsharing \
                                              --trials 1 \
                                              --combs \
                                              --combs-max-samples $LIMIT_MAX_SAMPLES \
                                              --datasets $DATASETS
    done
    cat $prefix*"numapps"* > $prefix"-all-"$MAX_NUM_APPS
done


