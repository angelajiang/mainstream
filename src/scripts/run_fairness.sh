DATASETS="cars cats flowers pedestrian"
NUM_APPS=16
# BUDGET_OPTIONS="100 150 200 250"
# BUDGET_OPTIONS+=" 25 50 75 125 175"
BUDGET_OPTIONS="25 50 75 100 125 150 175"
BUDGET_OPTIONS+=" 200 225 250"
# BUDGET_OPTIONS="25 50"
for BUDGET in $BUDGET_OPTIONS; do
    echo "Budget: $BUDGET"
    # pypy \
    #     src/scheduler/run_scheduler_simulator.py \
    #     $NUM_APPS \
    #     ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-greedy-b$BUDGET \
    #     --scheduler greedy \
    #     --datasets $DATASETS \
    #     --budget $BUDGET
    echo "Hifi-maxmin"
    pypy \
        src/scheduler/run_scheduler_simulator.py \
        $NUM_APPS \
        ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-maxmin-b$BUDGET \
        --scheduler hifi \
        --agg min \
        --datasets $DATASETS \
        --budget $BUDGET
    # echo "Hifi-avg"
    # pypy \
    #     src/scheduler/run_scheduler_simulator.py \
    #     $NUM_APPS \
    #     ../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-avg-b$BUDGET \
    #     --scheduler hifi \
    #     --agg avg \
    #     --datasets $DATASETS \
    #     --budget $BUDGET
done