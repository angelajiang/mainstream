DATA_DIR="data/cpp"
RUN_ID="latency.v0"
VERBOSE=0
NUM_APPS=10
SWEEP_NUM_APPS=1
NUM_SETUPS=1
STREAM_FPS=1
SETUP_CONFIG="config/scheduler/setup.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SCHEDULER_TYPE="hifi"
SIMULATOR=1

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS_RANGE \
                                        -sn $SWEEP_NUM_APPS \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG

g++ -std=c++0x  src/scheduler/cpp/exhaustive_search.cpp \
                src/scheduler/cpp/schedule.cpp \
                src/scheduler/cpp/schedule_unit.cpp \
                && ./a.out $DATA_DIR $RUN_ID
