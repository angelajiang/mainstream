#!/bin/bash
SCHEDULER_TYPE="greedy"
DATA_DIR="data/cpp/"
RUN_ID="debug2.v0"
VERBOSE=0
NUM_APPS_RANGE=4
NUM_SETUPS=5
STREAM_FPS=5
SETUP_CONFIG="config/scheduler/setup.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SIMULATOR=1
SWEEP=0
CXXFLAGS="-O3 -g3 -fno-pie"
CXXFLAGS+=" -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free"

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

python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                  -o $DATA_DIR \
                                                  -r $RUN_ID \
                                                  -f $SETUPS_FILE \
                                                  -t $SCHEDULER_TYPE \
                                                  -s $SIMULATOR
