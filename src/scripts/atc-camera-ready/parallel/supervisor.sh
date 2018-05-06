
NUM_NODES=5
SCRIPT="src/scripts/atc-camera-ready/parallel/test.sh"
DATA_DIR="data/cpp/debug"
BUDGETS="50 100 150 200 250 300"
SCHEDULERS="stems_cpp"
MODES="mainstream"

for NUM_APPS in 2
do
  EXPERIMENT_ID="debug-"$NUM_APPS".v1"
  SETUPS_FILE=$DATA_DIR"/setups."$EXPERIMENT_ID
  python src/scripts/atc-camera-ready/parallel/balance.py \
                    --setups_file $SETUPS_FILE \
                    -n $NUM_NODES \
                    -d $DATA_DIR \
                    -e $EXPERIMENT_ID \
                    -b $BUDGETS \
                    -s $SCRIPT \
                    -S $SCHEDULERS
done

