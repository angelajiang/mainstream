DATA_DIR="data/cpp/"
#DATASETS="cars cats flowers pedestrian"
DATASETS="cars cats"
RUN_ID="test"
BUDGET=300
VERBOSE=0
NUM_APPS=2
python src/scheduler/exhaustive_search.py -v $VERBOSE \
                                          -o $DATA_DIR \
                                          -d $DATASETS \
                                          -r $RUN_ID \
                                          -n $NUM_APPS \
                                          -b $BUDGET
g++ src/scheduler/cpp/exhaustive_search.cpp \
    src/scheduler/cpp/schedule.cpp \
    src/scheduler/cpp/schedule_unit.cpp \
    && ./a.out
