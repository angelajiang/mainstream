# Scheduler defaults to hifi, but can be overridden via first argument
SCHEDULER_TYPE=${1:-"hifi"}
DATA_DIR="test/tmp/$SCHEDULER_TYPE"
RUN_ID="debug-test1.v0"
VERBOSE=0
NUM_APPS=3
SWEEP_NUM_APPS=1
NUM_SETUPS=1
STREAM_FPS=5
SETUP_CONFIG="config/scheduler/setup_fast.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SIMULATOR=1

# Stop the script if any command returns an error
set -e

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS \
                                        -sn $SWEEP_NUM_APPS \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG

if [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
  g++ -std=c++14 -g3 -O3 -fno-pie -L/usr/lib -lprofiler -ltcmalloc \
    -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free \
    src/scheduler/cpp/stem_search.cpp \
    src/scheduler/cpp/schedule.cpp \
    src/scheduler/cpp/schedule_unit.cpp \
    && ./a.out $DATA_DIR $RUN_ID
else
  python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                    -o $DATA_DIR \
                                                    -r $RUN_ID \
                                                    -f $SETUPS_FILE \
                                                    -t $SCHEDULER_TYPE \
                                                    -s $SIMULATOR
fi

g++ -std=c++0x -O3 src/scheduler/cpp/exhaustive_search.cpp \
                   src/scheduler/cpp/schedule.cpp \
                   src/scheduler/cpp/schedule_unit.cpp \
                   && ./a.out $DATA_DIR $RUN_ID
