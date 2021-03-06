#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR="data/cpp/atc/050818"
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

#NUM_APPS=20
#BUDGET=150

for BUDGET in 100 150 200 250 300 350
do
    for CORR in ind emp dep
    do
        for NUM_APPS in 2 4 6 8 10 15 20 25 30 
        do
            RUN_ID="050318-"$NUM_APPS"-"$CORR".v1"
            SETUP_CONFIG="config/scheduler/050318-"$CORR".v1"
            SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID

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
                && ./a.out $DATA_DIR $RUN_ID $BUDGET
            elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
              g++ -std=c++14 $CXXFLAGS \
                src/scheduler/cpp/stem_search.cpp \
                src/scheduler/cpp/data.cpp \
                src/scheduler/cpp/types/*.cpp \
                && ./a.out $DATA_DIR $RUN_ID $BUDGET
            else
                for MODE in "mainstream" "maxsharing" "nosharing"
                do 
                    python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
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
done

