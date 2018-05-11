
CLUSTER="mycluster2"
NUM_NODES=1
DATA_DIR="/homes/ahjiang/src/mainstream/data/cpp/atc/050318"
SCHEDULERS="exhaustive"
MODES="mainstream"
SCRIPT="/homes/ahjiang/src/mainstream/src/scripts/atc-camera-ready/parallel/run.sh"
KEY_FILE="/homes/ahjiang/.ssh/id_rsa"
CXXFLAGS="-O3 -g3 -fno-pie -lstdc++"

g++ -o exhaustive -std=c++14 $CXXFLAGS \
  src/scheduler/cpp/exhaustive_search.cpp \
  src/scheduler/cpp/schedule.cpp \
  src/scheduler/cpp/schedule_unit.cpp

BUDGETS="100 150 200 250 300"
NUM_APPS=7
EXPERIMENT_ID="050318-"$NUM_APPS".v1"
SETUPS_FILE=$DATA_DIR"/setups."$EXPERIMENT_ID
python /homes/ahjiang/src/mainstream/src/scripts/atc-camera-ready/parallel/balance.py \
                  --setups_file $SETUPS_FILE \
                  -c $CLUSTER \
                  -n $NUM_NODES \
                  -d $DATA_DIR \
                  -e $EXPERIMENT_ID \
                  -b $BUDGETS \
                  -k $KEY_FILE \
                  -s $SCRIPT \
                  -S $SCHEDULERS

BUDGETS="50 100 150 200 250 300"
for NUM_APPS in 8 9 10 15 20 25 30
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
                    -k $KEY_FILE \
                    -s $SCRIPT \
                    -S $SCHEDULERS
done

