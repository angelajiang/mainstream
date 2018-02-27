DATA_DIR="data/cpp/"
DATASETS="cars cats flowers pedestrian"
python src/scheduler/exhaustive_search.py -o $DATA_DIR -d $DATASETS
