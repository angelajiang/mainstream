#!/bin/bash
SCHEDULER_TYPE="path"
VERBOSE=0
SIMULATOR=1
SWEEP=0
CXXFLAGS="-O3 -g3 -fno-pie"
CXXFLAGS+=" -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free"

# Think about these params
NUM_APPS_RANGE=8
NUM_SETUPS=10
DATA_DIR="data/cpp/"
RUN_ID="p10.v0"
SETUP_CONFIG="config/scheduler/setup.v0"
STREAM_FPS=5

declare -a DOM_PRUNE_LIST=(1 10 20 40)
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID

# Stop the script if any command returns an error
set -e

mkdir -p $DATA_DIR/schedules

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS_RANGE \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -sn $SWEEP \
                                        -c $SETUP_CONFIG

for i in ${DOM_PRUNE_LIST[@]}; do
    python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                      -o $DATA_DIR \
                                                      -r $RUN_ID \
                                                      -f $SETUPS_FILE \
                                                      -t $SCHEDULER_TYPE \
                                                      -p $i \
                                                      -s $SIMULATOR \
                                                      -i "${i//.}"
done
