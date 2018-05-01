DATASETS="cars cats train pedestrian"
NUM_APPS=16
OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180430-train-aug-flipped_ratio_nosharing"
OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/180430-train"

python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        $OUTFILE_PREFIX-maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-greedy-b*-mainstream-simulator \
    --o $OUT_DIR"/aug_ratio_nosharing_flipped_ratioed-fairness_results.pkl" \
    --scheduler hifi \
    --metric-rescale ratio_nosharing_flipped \
    --verbose 1 \
    --datasets $DATASETS \
