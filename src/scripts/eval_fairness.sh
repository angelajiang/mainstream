DATASETS="cars cats flowers pedestrian"
BUDGET=300
NUM_APPS=16
python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-maxmin-b*-mainstream-simulator \
        ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-avg-b*-mainstream-simulator \
        ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-greedy-b*-mainstream-simulator \
    --scheduler hifi \
    --datasets $DATASETS \
    --budget $BUDGET

# python src/scheduler/eval_fairness.py -n 12 -d cars cats flowers pedestrian \
#     ../mainstream-analysis/