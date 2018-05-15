#!/bin/bash
SCHEDULER_TYPE=$1
DATA_DIR=${2:-"test/tmp/$SCHEDULER_TYPE"}
RUN_ID="debug.v1"
VERBOSE=0
BUDGET=100
SETUPS_FILE=$DATA_DIR"/setups."$RUN_ID
SIMULATOR=1

# Stop the script if any command returns an error
set -e

if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
    make bin/exhaustive && ./bin/exhaustive $DATA_DIR $RUN_ID $BUDGET
elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
    make bin/stem_search && ./bin/stem_search $DATA_DIR $RUN_ID $BUDGET
else
    python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                      -o $DATA_DIR \
                                                      -r $RUN_ID \
                                                      -f $SETUPS_FILE \
                                                      -t $SCHEDULER_TYPE \
                                                      -b $BUDGET \
                                                      -s $SIMULATOR
fi
