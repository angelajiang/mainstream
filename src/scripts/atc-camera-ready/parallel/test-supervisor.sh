
CLUSTER="mycluster"
NUM_NODES=5
DATA_DIR="data/cpp/debug"
BUDGETS="50 100 150 200 250 300"
SCHEDULERS="stems_cpp"
MODES="mainstream"
SCRIPT="src/scripts/atc-camera-ready/parallel/run.sh"

g++ -std=c++0x -o exhaustive $CXXFLAGS \
  src/scheduler/cpp/exhaustive_search.cpp \
  src/scheduler/cpp/data.cpp \
  src/scheduler/cpp/types/*.cpp

g++ -std=c++14 -o stems_cpp $CXXFLAGS \
  src/scheduler/cpp/stem_search.cpp \
  src/scheduler/cpp/data.cpp \
  src/scheduler/cpp/types/*.cpp

for NUM_APPS in 2
do
  EXPERIMENT_ID="debug-"$NUM_APPS".v1"
  SETUPS_FILE=$DATA_DIR"/setups."$EXPERIMENT_ID
  python src/scripts/atc-camera-ready/parallel/balance.py \
                    --setups_file $SETUPS_FILE \
                    -c $CLUSTER \
                    -n $NUM_NODES \
                    -d $DATA_DIR \
                    -e $EXPERIMENT_ID \
                    -b $BUDGETS \
                    -s $SCRIPT \
                    -S $SCHEDULERS
done

