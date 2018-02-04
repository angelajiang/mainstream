#!/bin/bash
# Run fairness for F1-score
MAX_NUM_APPS=32
METRIC=f1
OUTFILE_PREFIX=../mainstream-analysis/output/streamer/scheduler/atc/$METRIC/$METRIC-fairness-4hybrid
# Archive old file
mv $OUTFILE_PREFIX-mainstream-simulator $OUTFILE_PREFIX-mainstream-simulator-`date +%Y%m%d-%H%M`
python src/scheduler/run_scheduler_simulator.py \
        $MAX_NUM_APPS \
        $OUTFILE_PREFIX \
        --metric $METRIC \
        --datasets pedestrian cars flowers cats \
        --fairness
