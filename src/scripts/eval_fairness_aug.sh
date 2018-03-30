DATASETS="cars cats flowers pedestrian"
BUDGET=300
NUM_APPS=16
OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-aug_ratio_nosharing"
OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2"

python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        $OUTFILE_PREFIX-maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-greedy-b*-mainstream-simulator \
    --o $OUT_DIR"/aug_ratio_nosharing_ratioed-fairness_results.pkl" \
    --scheduler hifi \
    --metric-rescale ratio_nosharing \
    --datasets $DATASETS \
    --budget $BUDGET

python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        $OUTFILE_PREFIX-maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-greedy-b*-mainstream-simulator \
    --o $OUT_DIR"/aug_ratio_nosharing-fairness_results.pkl" \
    --scheduler hifi \
    --datasets $DATASETS \
    --budget $BUDGET

