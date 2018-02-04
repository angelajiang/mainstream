#!/bin/bash
MAX_NUM_APPS=30
METRIC=f1
python src/scheduler/run_scheduler_sim_fair.py \
        $MAX_NUM_APPS \
        0 \
        ../mainstream-analysis/output/streamer/scheduler/atc/$METRIC/$METRIC-fairness \
        --metric $METRIC \
        --fairness
