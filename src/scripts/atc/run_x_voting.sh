#!/bin/bash
MAX_NUM_APPS=30
#SEM_CMD1=sem -j+0
#SEM_CMD2=sem --wait

#if [[ ! type sem > /dev/null ]]; then
#    echo "sem (part of GNU parallel not installed)"
#    echo "Try 'pkg install parallel'"
#    echo "processing without it"
#    SEM_CMD1=
#    SEM_CMD2=
#fi
#    for j in f1 fnr fpr; do
for j in f1; do
    for DATASET in pedestrian train; do
        for i in 1 2 3 4 5 6 7; do
            sem -j+0 python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-$DATASET-500 -m $j --x-vote $i --datasets $DATASET > log/atc/$j-$DATASET-500-x$i-mainstream-simulator.out
        done
        # sem -j+0 python src/scheduler/run_scheduler_simulator.py $MAX_NUM_APPS ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-$DATASET-500 -m $j --datasets $DATASET > log/atc/$j-$DATASET-500-mainstream-simulator.out
    done
done
sem --wait
#$SEM_CMD2
