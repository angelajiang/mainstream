npz="/datasets/BigLearning/ahjiang/bb/npz/urban-tracker-stmarc-pedestrian-training.npz"
labels="/datasets/BigLearning/ahjiang/bb/urban-tracker/labels/pedestrian-label.txt"
model_prefix="/users/ahjiang/models/detection/yad2k/pedestrian/yolov2-stmarc-pedestrian"
test_path="/datasets/BigLearning/ahjiang/bb/npz/urban-tracker-stmarc-pedestrian-test.npz"
model_prefix="/users/ahjiang/models/detection/yad2k/pedestrian/yolov2-stmarc-pedestrian"
result_path="/users/ahjiang/src/mainstream-analysis/output/bb/raw/training/urban-tracker/stmarc/urban-tracker-stmarc-pedestrian-e60-1"

step=5
start=5
end=5
num_trials=1

j=1

for i in `seq $start $step $end`;
do
    python -u src/training/train_yad2k.py  -d $npz -c $labels -p $model_prefix -n $i --num_epochs $j --num_trials $num_trials --test $test_path -r $result_path
    echo "Results written to: "$result_path
done

