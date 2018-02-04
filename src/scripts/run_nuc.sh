#!/bin/bash
MAX_NUM_APPS=30
dataset=trains
for metric in f1 fnr fpr; do
    python src/scheduler/run_scheduler.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$metric/$metric-$dataset -m $metric --version 1 2 --trials 1
done
