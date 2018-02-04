#!/bin/bash
MAX_NUM_APPS=30
DATASET=trains
SEM_CMD1=sem -j+0 
SEM_CMD2=sem --wait
if [[ ! type sem > /dev/null ]]; then
    echo "sem (part of GNU parallel not installed)"
    echo "Try 'pkg install parallel'"
    echo "processing without it"
    SEM_CMD1=
    SEM_CMD2=
fi
for i in 0 1 2 3; do
    for j in f1 fnr fpr; do
        $SEM_CMD1 python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-$DATASET-500 -m $j --x-vote $i --datasets $DATASET
    done
done
$SEM_CMD2
