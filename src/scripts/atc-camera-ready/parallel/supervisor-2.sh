
CLUSTER="mycluster2"
NUM_NODES=100
DATA_DIR="/homes/ahjiang/src/mainstream/data/cpp/atc/050318"
BUDGETS="50 100 150 200 250 300"
SCHEDULERS="exhaustive"
MODES="mainstream"
SCRIPT="/homes/ahjiang/src/mainstream/src/scripts/atc-camera-ready/parallel/run.sh"

g++ -std=c++0x -o exhaustive $CXXFLAGS \
  src/scheduler/cpp/exhaustive_search.cpp \
  src/scheduler/cpp/data.cpp \
  src/scheduler/cpp/types/*.cpp

for NUM_APPS in 2 3 4 5 6 7 8 9 10 15 20 25 30
do
  EXPERIMENT_ID="050318-"$NUM_APPS".v1"
  SETUPS_FILE=$DATA_DIR"/setups."$EXPERIMENT_ID
  python /homes/ahjiang/src/mainstream/src/scripts/atc-camera-ready/parallel/balance.py \
                    --setups_file $SETUPS_FILE \
                    -c $CLUSTER \
                    -n $NUM_NODES \
                    -d $DATA_DIR \
                    -e $EXPERIMENT_ID \
                    -b $BUDGETS \
                    -s $SCRIPT \
                    -S $SCHEDULERS
done

