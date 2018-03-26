# DATASETS="cars cats flowers pedestrian"
DATASETS="pedestrian flowers cats cars"
OUT_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-reversed"
NUM_APPS=16
BUDGET_OPTIONS="25 50 75 100 125 150 175"
BUDGET_OPTIONS+=" 200 225 250"
# BUDGET_OPTIONS="25 50"
for BUDGET in $BUDGET_OPTIONS; do
    echo "Budget: $BUDGET"
    # echo "Greedy"
    # pypy \
    #     src/scheduler/run_scheduler_simulator.py \
    #     $NUM_APPS \
    #     $OUT_PREFIX-greedy-b$BUDGET \
    #     --scheduler greedy \
    #     --datasets $DATASETS \
    #     --budget $BUDGET
    # echo "Hifi-maxmin"
    # pypy \
    #     src/scheduler/run_scheduler_simulator.py \
    #     $NUM_APPS \
    #     $OUT_PREFIX-maxmin-b$BUDGET \
    #     --scheduler hifi \
    #     --agg min \
    #     --datasets $DATASETS \
    #     --budget $BUDGET
    echo "Hifi-avg"
    pypy \
        src/scheduler/run_scheduler_simulator.py \
        $NUM_APPS \
        $OUT_PREFIX-avg-b$BUDGET \
        --scheduler hifi \
        --agg avg \
        --datasets $DATASETS \
        --budget $BUDGET
done