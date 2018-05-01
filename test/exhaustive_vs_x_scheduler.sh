#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR=${2:-"test/tmp/$SCHEDULER_TYPE"}
RUN_ID="debug.v1"
VERBOSE=0
NUM_APPS_RANGE=3
BUDGET=100
NUM_SETUPS=1
STREAM_FPS=5
SETUP_CONFIG="config/scheduler/setup_fast.v1"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SIMULATOR=1
CXXFLAGS="-O3 -g3 -fno-pie -lprofiler -ltcmalloc"
CXXFLAGS+=" -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free"

# Stop the script if any command returns an error
set -e

mkdir -p $DATA_DIR/schedules

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS \
                                        -sn $SWEEP_NUM_APPS \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG

if [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
  g++ -std=c++14 $CXXFLAGS \
    src/scheduler/cpp/stem_search.cpp \
    src/scheduler/cpp/data.cpp \
    src/scheduler/cpp/types/*.cpp \
    && ./a.out $DATA_DIR $RUN_ID $BUDGET
else
  python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                    -o $DATA_DIR \
                                                    -r $RUN_ID \
                                                    -f $SETUPS_FILE \
                                                    -t $SCHEDULER_TYPE \
                                                    -b $BUDGET \
                                                    -s $SIMULATOR
fi

g++ -std=c++0x $CXXFLAGS \
  src/scheduler/cpp/exhaustive_search.cpp \
  src/scheduler/cpp/data.cpp \
  src/scheduler/cpp/types/*.cpp \
  && ./a.out $DATA_DIR $RUN_ID $BUDGET
