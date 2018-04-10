ON_GREEDY=${1:-0}
ON_MAXMIN=${2:-0}
ON_AVG=${3:-1}
DATASETS="cars cats flowers pedestrian"
# DATASETS="pedestrian flowers cats cars"
# DATASETS="pedestrian cats"
OUT_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180401"
NUM_APPS=16
BUDGET_OPTIONS="25 50 75 100 125 150 175"
BUDGET_OPTIONS+=" 200"
# BUDGET_OPTIONS+=" 225 250"
for BUDGET in $BUDGET_OPTIONS; do
    echo "Budget: $BUDGET"
    if [[ $ON_GREEDY -eq 1 ]]; then
        echo "Greedy"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-greedy-b$BUDGET \
            --scheduler greedy \
            --datasets $DATASETS \
            --budget $BUDGET
    fi
    if [[ $ON_MAXMIN -eq 1 ]]; then
        echo "Hifi-maxmin"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-maxmin-b$BUDGET \
            --scheduler hifi \
            --agg min \
            --datasets $DATASETS \
            --budget $BUDGET
    fi
    if [[ $ON_AVG -eq 1 ]]; then
        echo "Hifi-avg"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-avg-b$BUDGET \
            --scheduler hifi \
            --agg avg \
            --datasets $DATASETS \
            --budget $BUDGET
    fi
done