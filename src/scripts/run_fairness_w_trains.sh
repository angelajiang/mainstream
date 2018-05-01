ON_GREEDY=${1:-0}
ON_MAXMIN=${2:-0}
ON_AVG=${3:-1}
ON_MAXMIN_STEMS=${4:-1}
ON_AVG_STEMS=${5:-0}
DATASETS="cars cats train pedestrian"
# DATASETS="pedestrian flowers cats cars"
# DATASETS="pedestrian cats"
# OUT_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180401-train"
OUT_PREFIX="../mainstream-analysis/output/streamer/scheduler/18Q2/scheduler-180430-train"
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
            --verbose 1 \
            --budget $BUDGET
    fi
    if [[ $ON_MAXMIN -eq 1 ]]; then
        echo "Hifi-maxmin"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-hifi_maxmin-b$BUDGET \
            --scheduler hifi \
            --agg min \
            --datasets $DATASETS \
            --verbose 1 \
            --budget $BUDGET
    fi
    if [[ $ON_AVG -eq 1 ]]; then
        echo "Hifi-avg"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-hifi_avg-b$BUDGET \
            --scheduler hifi \
            --agg avg \
            --datasets $DATASETS \
            --verbose 1 \
            --budget $BUDGET
    fi
    if [[ $ON_MAXMIN_STEMS -eq 1 ]]; then
        echo "Stems-maxmin"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-stems_maxmin-b$BUDGET \
            --scheduler stems \
            --agg min \
            --datasets $DATASETS \
            --verbose 1 \
            --budget $BUDGET
    fi
    if [[ $ON_AVG_STEMS -eq 1 ]]; then
        echo "Stems-avg"
        pypy \
            src/scheduler/run_scheduler_simulator.py \
            $NUM_APPS \
            $OUT_PREFIX-stems_avg-b$BUDGET \
            --scheduler stems \
            --agg avg \
            --datasets $DATASETS \
            --verbose 1 \
            --budget $BUDGET
    fi
done