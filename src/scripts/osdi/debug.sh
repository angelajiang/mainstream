#!/bin/bash
NUM_APPS_RANGE=10
OPTIMIZE_METRIC=f1
DATASETS="bus schoolbus redcar scramble"
OUTFILE_PREFIX=../mainstream-analysis/output/streamer/scheduler/debug
SCHEDULER=hifi

for NUM_APPS in $(seq 4 $NUM_APPS_RANGE)
do
  echo $NUM_APPS
  for MODE in mainstream maxsharing nosharing
  do
    echo $MODE
  done
done
