#!/bin/bash
NUM_APPS_RANGE=30
OPTIMIZE_METRIC=f1
DATASETS="bus schoolbus redcar scramble"
OUTFILE_PREFIX=../mainstream-analysis/output/streamer/scheduler/debug
SCHEDULER=greedy

for NUM_APPS in $(seq 2 $NUM_APPS_RANGE)
do
  for MODE in mainstream maxsharing nosharing
  do
  python src/scheduler/run_scheduler_simulator.py \
      $NUM_APPS \
      $OUTFILE_PREFIX/iii-$SCHEDULER-$MODE \
      --metric $OPTIMIZE_METRIC \
      --datasets $DATASETS \
      --mode $MODE \
      --budget 350 \
      --scheduler $SCHEDULER
  done
done
