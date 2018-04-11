#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR="test/tmp/$SCHEDULER_TYPE"
RUN_ID="debug.v0"
VERBOSE=0
NUM_APPS_RANGE=$2
NUM_SETUPS=5
STREAM_FPS=5
SETUP_CONFIG="config/scheduler/setup.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SIMULATOR=1

# Stop the script if any command returns an error
set -e

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS_RANGE \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG

if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
    g++ -std=c++0x -O3 src/scheduler/cpp/exhaustive_search.cpp \
                       src/scheduler/cpp/schedule.cpp \
                       src/scheduler/cpp/schedule_unit.cpp \
                       && ./a.out $DATA_DIR $RUN_ID
elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
  g++ -std=c++14 -O3 src/scheduler/cpp/stem_search.cpp \
                     src/scheduler/cpp/schedule.cpp \
                     src/scheduler/cpp/schedule_unit.cpp \
                     && ./a.out $DATA_DIR $RUN_ID
else
    python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                      -o $DATA_DIR \
                                                      -r $RUN_ID \
                                                      -f $SETUPS_FILE \
                                                      -t $SCHEDULER_TYPE \
                                                      -s $SIMULATOR \
                                                      -n $NUM_APPS_RANGE
fi
