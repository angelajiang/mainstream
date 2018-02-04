#!/bin/bash
MAX_NUM_APPS=30
OPTIMIZE_METRIC=f1
LIMIT_MAX_SAMPLES=40
X_VOTING=0
DATASETS=pedestrian cars flowers cats
SEM_CMD1=sem -j+0 
SEM_CMD2=sem --wait
if [[ ! type sem > /dev/null ]]; then
    echo "sem (part of GNU parallel not installed)"
    echo "Try 'pkg install parallel'"
    echo "processing without it"
    SEM_CMD1=
    SEM_CMD2=
fi
for i in $(seq 1 $MAX_NUM_APPS); do
    $SEM_CMD1 python src/scheduler/run_scheduler_simulator.py $i ../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/$OPTIMIZE_METRIC-combinations-$i --combs --combs-max-samples $LIMIT_MAX_SAMPLES --metric $OPTIMIZE_METRIC --x-vote $X_VOTING --datasets $DATASETS
done
$SEM_CMD2
cat ../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/$OPTIMIZE_METRIC-combinations-*-mainstream-simulator > ../mainstream-analysis/output/streamer/scheduler/atc/$OPTIMIZE_METRIC/$OPTIMIZE_METRIC-combo-mainstream-simulator
