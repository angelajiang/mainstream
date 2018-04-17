DATA_DIR="data/cpp/"
RUN_ID="041618.v0"
VERBOSE=0
NUM_APPS=10
NUM_SETUPS=20
STREAM_FPS=10
SETUP_CONFIG="config/scheduler/setup.v0"
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SCHEDULER_TYPE="greedy"
SWEEP=0
SIMULATOR=1

# Only need to generate this once
python src/scheduler/generate_setups.py -r $RUN_ID \
                                        -n $NUM_APPS \
                                        -o $DATA_DIR \
                                        -s $NUM_SETUPS \
                                        -f $STREAM_FPS \
                                        -c $SETUP_CONFIG \
                                        -sn $SWEEP

for MODE in maxsharing mainstream nosharing
do
python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                  -o $DATA_DIR \
                                                  -r $RUN_ID \
                                                  -f $SETUPS_FILE \
                                                  -t $SCHEDULER_TYPE \
                                                  -s $SIMULATOR \
                                                  --mode $MODE
done

SCHEDULER_TYPE="stems"
MODE="mainstream"
python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                  -o $DATA_DIR \
                                                  -r $RUN_ID \
                                                  -f $SETUPS_FILE \
                                                  -t $SCHEDULER_TYPE \
                                                  -s $SIMULATOR \
                                                  --mode $MODE

