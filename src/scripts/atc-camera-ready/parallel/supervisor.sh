
CLUSTER="mycluster"
NUM_NODES=50
DATA_DIR="/homes/ahjiang/src/mainstream/data/cpp/atc/050318"
SCHEDULERS="stems_cpp"
MODES="mainstream"
SCRIPT="/homes/ahjiang/src/mainstream/src/scripts/atc-camera-ready/parallel/run.sh"
KEY_FILE="/homes/ahjiang/.ssh/id_rsa"
CXXFLAGS="-O3 -g3 -fno-pie -lstdc++"

g++ -std=c++14 -o stems_cpp $CXXFLAGS \
  src/scheduler/cpp/stem_search.cpp \
  src/scheduler/cpp/data.cpp \
  src/scheduler/cpp/types/*.cpp

BUDGETS="50 100 150 200 250 300"
for NUM_APPS in 7 8 9 10 15 20 25 30
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

