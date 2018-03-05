DATA_DIR="data/cpp/"
#DATASETS="cars cats"
DATASETS="cars cats flowers pedestrian"
RUN_ID="test"
BUDGET_RANGE=500
VERBOSE=0
NUM_APPS_RANGE=8
python src/scheduler/exhaustive_search.py -v $VERBOSE \
                                          -o $DATA_DIR \
                                          -d $DATASETS \
                                          -r $RUN_ID \
                                          -n $NUM_APPS_RANGE \
                                          -b $BUDGET_RANGE
g++ src/scheduler/cpp/exhaustive_search.cpp \
    src/scheduler/cpp/schedule.cpp \
    src/scheduler/cpp/schedule_unit.cpp \
    && ./a.out
