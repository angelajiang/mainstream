DATASETS="cars cats flowers pedestrian"
BUDGET=300
NUM_APPS=16
# OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler"
OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-reversed"
# OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/fairness_results.pkl"
OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/reversed-fairness_results.pkl"
python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        $OUTFILE_PREFIX-maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-greedy-b*-mainstream-simulator \
    --o $OUT_DIR \
    --scheduler hifi \
    --datasets $DATASETS \
    --budget $BUDGET

# python src/scheduler/eval_fairness.py -n 12 -d cars cats flowers pedestrian \
#     ../mainstream-analysis/