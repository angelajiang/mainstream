#!/bin/bash
SCHEDULER_TYPE=$1
NUM_APPS=$2
DATA_DIR="data/cpp"
VERBOSE=0
STREAM_FPS=5
SIMULATOR=1
SWEEP=0

CXXFLAGS="-O3 -g3 -fno-pie"
CXXFLAGS+=" -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free"

# Stop the script if any command returns an error
set -e

mkdir -p $DATA_DIR/schedules

for BUDGET in 100 150 200 250 300
do
    RUN_ID="041718-$BUDGET-"$NUM_APPS".v0"
    SETUP_CONFIG="config/scheduler/041718-$BUDGET.v0"
    SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
    NUM_SETUPS=50

    # Only need to generate this once
    python src/scheduler/generate_setups.py -r $RUN_ID \
                                            -n $NUM_APPS \
                                            -o $DATA_DIR \
                                            -s $NUM_SETUPS \
                                            -f $STREAM_FPS \
                                            -sn $SWEEP \
                                            -c $SETUP_CONFIG

    if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
      g++ -std=c++0x $CXXFLAGS \
        src/scheduler/cpp/exhaustive_search.cpp \
        src/scheduler/cpp/data.cpp \
        src/scheduler/cpp/types/*.cpp \
        && ./a.out $DATA_DIR $RUN_ID
    elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
      g++ -std=c++14 $CXXFLAGS \
        src/scheduler/cpp/stem_search.cpp \
        src/scheduler/cpp/data.cpp \
        src/scheduler/cpp/types/*.cpp \
        && ./a.out $DATA_DIR $RUN_ID
    else
        for MODE in "maxsharing" "nosharing"
        do 
            python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                              -o $DATA_DIR \
                                                              -r $RUN_ID \
                                                              -f $SETUPS_FILE \
                                                              -t $SCHEDULER_TYPE \
                                                              --mode $MODE \
                                                              -s $SIMULATOR
        done
    fi
done

