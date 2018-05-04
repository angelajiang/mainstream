#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR=${3:-"test/tmp/$SCHEDULER_TYPE"}
RUN_ID="debug.v1"
NUM_APPS_RANGE=$2
NUM_SETUPS=5
STREAM_FPS=5
SETUP_CONFIG=${4:-"config/scheduler/setup.v1"}

# Stop the script if any command returns an error
set -e

mkdir -p $DATA_DIR/schedules

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS_RANGE \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG
