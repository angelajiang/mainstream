#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR="data/cpp/atc"
VERBOSE=0
STREAM_FPS=10
SIMULATOR=1
SWEEP=0
NUM_SETUPS=100

CXXFLAGS="-O3 -g3 -fno-pie"
CXXFLAGS+=" -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free"

# Stop the script if any command returns an error
set -e

mkdir -p $DATA_DIR
mkdir -p $DATA_DIR/schedules
mkdir -p $DATA_DIR/logs

if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
  g++ -std=c++0x $CXXFLAGS \
    src/scheduler/cpp/exhaustive_search.cpp \
    src/scheduler/cpp/data.cpp \
    src/scheduler/cpp/types/*.cpp
elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
  g++ -std=c++14 $CXXFLAGS \
    src/scheduler/cpp/stem_search.cpp \
    src/scheduler/cpp/data.cpp \
    src/scheduler/cpp/types/*.cpp
fi

for NUM_APPS in 2 3 4 5 6 7 8 9 10 15 20 25 30
do
    RUN_ID="042518-"$NUM_APPS".v1"
    SETUP_CONFIG="config/scheduler/042518.v1"

    # Only need to generate this once
    python src/scheduler/generate_setups.py -r $RUN_ID \
                                            -n $NUM_APPS \
                                            -o $DATA_DIR \
                                            -s $NUM_SETUPS \
                                            -f $STREAM_FPS \
                                            -sn $SWEEP \
                                            -c $SETUP_CONFIG

done


for NUM_APPS in 2 3 4 5 6 7 8 9 10 15 20 25 30
do
    RUN_ID="042518-"$NUM_APPS".v1"
    SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
    for BUDGET in 50 100 150 200 250 300
    do
      if [[ "$SCHEDULER_TYPE" == "exhaustive" ]] || [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
        sem -j+0 ./a.out $DATA_DIR $RUN_ID $BUDGET
      else
          for MODE in "mainstream" "maxsharing" "nosharing"
          do
              sem -j+0 python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                                -o $DATA_DIR \
                                                                -r $RUN_ID \
                                                                -f $SETUPS_FILE \
                                                                -t $SCHEDULER_TYPE \
                                                                -b $BUDGET \
                                                                --mode $MODE \
                                                                -s $SIMULATOR
          done
      fi
    done
done
sem --wait

