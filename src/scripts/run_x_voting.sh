#!/bin/bash
MAX_NUM_APPS=30
DATASET=trains
for i in 0 1 2 3; do
    for j in f1 fnr fpr; do
        sem -j+0 python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-$DATASET-500 -m $j --x-vote $i --datasets $DATASET
    done
done
sem --wait
