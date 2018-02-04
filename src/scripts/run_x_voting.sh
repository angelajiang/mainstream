#!/bin/bash
MAX_NUM_APPS=30
dataset=trains
for i in 0 1 2 3; do
    for j in f1 fnr fpr; do
        sem -j+0 python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-$dataset-500 -m $j --x-vote $i
    done
done
sem --wait
