DATA_DIR="data/cpp/"
DATASETS="cars cats flowers pedestrian"
RUN_ID="experiment"
BUDGET_RANGE=500
VERBOSE=0
NUM_APPS_RANGE=8
echo "Run ID: $RUN_ID"
#pypy src/scheduler/exhaustive_search.py -v $VERBOSE \
#                                          -o $DATA_DIR \
#                                          -d $DATASETS \
#                                          -r $RUN_ID \
#                                          -n $NUM_APPS_RANGE \
#                                          -b $BUDGET_RANGE \
#                                          -s greedy
#pypy src/scheduler/exhaustive_search.py -v $VERBOSE \
#                                            -o $DATA_DIR \
#                                            -d $DATASETS \
#                                            -r $RUN_ID \
#                                            -n $NUM_APPS_RANGE \
#                                            -b $BUDGET_RANGE \
#                                            -s hifi
g++ -std=c++0x  src/scheduler/cpp/exhaustive_search.cpp \
                src/scheduler/cpp/schedule.cpp \
                src/scheduler/cpp/schedule_unit.cpp \
                && ./a.out $RUN_ID
