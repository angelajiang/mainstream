# DATASETS="cars cats flowers pedestrian"
DATASETS="cars cats train pedestrian"
NUM_APPS=16
# OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler"
# OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-reversed"
# OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/fairness_results.pkl"
OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180401-train"
OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/180401-train/fairness_results.pkl"
# OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180401"
# OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/180401/fairness_results.pkl"
# OUTFILE_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180430-train"
# OUT_DIR="../mainstream-analysis/output/streamer/scheduler/18Q2/180430-train/fairness_results.pkl"
python \
    src/scheduler/eval_fairness.py \
    -n $NUM_APPS \
    --input \
        $OUTFILE_PREFIX-hifi_maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-hifi_avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-stems_maxmin-b*-mainstream-simulator \
        $OUTFILE_PREFIX-stems_avg-b*-mainstream-simulator \
        $OUTFILE_PREFIX-greedy-b*-mainstream-simulator \
    --o $OUT_DIR \
    --scheduler hifi \
    --datasets $DATASETS
# python src/scheduler/eval_fairness.py -n 12 -d cars cats flowers pedestrian \
#     ../mainstream-analysis/