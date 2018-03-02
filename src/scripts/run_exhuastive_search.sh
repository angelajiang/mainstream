DATA_DIR="data/cpp/"
DATASETS="cars cats flowers pedestrian"
RUN_ID="test"
BUDGET=300
python src/scheduler/exhaustive_search.py -o $DATA_DIR -d $DATASETS -r $RUN_ID -b $BUDGET
g++ src/scheduler/cpp/exhaustive_search.cpp \
    src/scheduler/cpp/schedule.cpp \
    src/scheduler/cpp/schedule_unit.cpp \
    && ./a.out
