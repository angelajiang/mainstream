#!/bin/bash
MAX_NUM_APPS=30
OPTIMIZE_METRIC=f1
LIMIT_MAX_SAMPLES=40
X_VOTING=0
DATASETS=pedestrian cars flowers cats
for i in $(seq 1 $MAX_NUM_APPS); do
    sem -j+0 python src/scheduler/run_scheduler_simulator.py $i ../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/$OPTIMIZE_METRIC-combinations-$i --combs --combs-max-samples $LIMIT_MAX_SAMPLES --metric $OPTIMIZE_METRIC --x-vote $X_VOTING --datasets $DATASETS
done
sem --wait
