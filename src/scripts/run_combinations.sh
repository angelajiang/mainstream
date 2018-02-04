#!/bin/bash
MAX_NUM_APPS=20
OPTIMIZE_METRIC=f1
LIMIT_MAX_SAMPLES=20
X_VOTING=0
for i in $(seq 1 $MAX_NUM_APPS); do
    sem -j+0 python src/scheduler/run_scheduler_simulator.py $i ../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/$OPTIMIZE_METRIC-combinations-$i --combs --combs-max-samples $LIMIT_MAX_SAMPLES --metric $OPTIMIZE_METRIC --x-vote $X_VOTING
done
sem --wait
