#!/bin/bash
MAX_NUM_APPS=30
DATASET=train
for metric in f1; do
    python src/scheduler/run_scheduler.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-$DATASET -m $metric --versions nosharing maxsharing --trials 1 --datasets $DATASET
done
