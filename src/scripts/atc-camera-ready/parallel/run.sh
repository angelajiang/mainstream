DATA_DIR=$1
EXPERIMENT_ID=$2
SETUPS_FILE=$3
BUDGET=$4
SCHEDULER_TYPE=$5

VERBOSE=0
SIMULATOR=1

mkdir -p $DATA_DIR
mkdir -p $DATA_DIR/schedules


if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
    ./exhaustive $DATA_DIR $EXPERIMENT_ID $BUDGET
elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
    ./stems_cpp $NUM_SCHEDULES $DATA_DIR $EXPERIMENT_ID $BUDGET
else
    for MODE in "mainstream" "maxsharing" "nosharing"
    do 
        python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
                                                          -o $DATA_DIR \
                                                          -r $EXPERIMENT_ID \
                                                          -f $SETUPS_FILE \
                                                          -t $SCHEDULER_TYPE \
                                                          -b $BUDGET \
                                                          --mode $MODE \
                                                          -s $SIMULATOR
    done
fi

#if [[ "$SCHEDULER_TYPE" == "exhaustive" ]]; then
#  g++ -std=c++0x $CXXFLAGS \
#    src/scheduler/cpp/exhaustive_search.cpp \
#    src/scheduler/cpp/data.cpp \
#    src/scheduler/cpp/types/*.cpp \
#    && ./a.out $DATA_DIR $EXPERIMENT_ID $BUDGET
#elif [[ "$SCHEDULER_TYPE" == "stems_cpp" ]]; then
#  g++ -std=c++14 $CXXFLAGS \
#    src/scheduler/cpp/stem_search.cpp \
#    src/scheduler/cpp/data.cpp \
#    src/scheduler/cpp/types/*.cpp \
#    && ./a.out $NUM_SCHEDULES $DATA_DIR $EXPERIMENT_ID $BUDGET
#else
#    for MODE in "mainstream" "maxsharing" "nosharing"
#    do 
#        python src/scheduler/run_scheduler_with_setups.py -v $VERBOSE \
#                                                          -o $DATA_DIR \
#                                                          -r $EXPERIMENT_ID \
#                                                          -f $SETUPS_FILE \
#                                                          -t $SCHEDULER_TYPE \
#                                                          -b $BUDGET \
#                                                          --mode $MODE \
#                                                          -s $SIMULATOR
#    done
#fi


