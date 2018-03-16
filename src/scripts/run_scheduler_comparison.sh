DATA_DIR="data/cpp/"
RUN_ID="031418.v0"
VERBOSE=0
NUM_APPS_RANGE=30
NUM_SETUPS=200
STREAM_FPS=10
SETUP_CONFIG="config/scheduler/031418.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SCHEDULER_TYPE="greedy"

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS_RANGE \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG

python src/scheduler/run_mainstream_simulator_with_setups.py -v $VERBOSE \
                                                             -o $DATA_DIR \
                                                             -r $RUN_ID \
                                                             -s $SETUPS_FILE \
                                                             -t $SCHEDULER_TYPE \
                                                             -n $NUM_APPS_RANGE

g++ -std=c++0x  src/scheduler/cpp/exhaustive_search.cpp \
                src/scheduler/cpp/schedule.cpp \
                src/scheduler/cpp/schedule_unit.cpp \
                && ./a.out $DATA_DIR $RUN_ID
