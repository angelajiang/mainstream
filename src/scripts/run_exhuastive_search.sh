DATA_DIR="data/cpp/"
DATASETS="cars cats flowers pedestrian"
RUN_ID="test"
python src/scheduler/exhaustive_search.py -o $DATA_DIR -d $DATASETS -r $RUN_ID
g++ src/scheduler/cpp/exhaustive_search.cpp && ./a.out
