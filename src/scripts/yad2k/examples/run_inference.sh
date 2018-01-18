labels="/datasets/BigLearning/ahjiang/bb/urban-tracker/labels/pedestrian-label.txt"
model_prefix="/users/ahjiang/models/detection/yad2k/pedestrian/yolov2-stmarc-pedestrian"
input="/datasets/BigLearning/ahjiang/bb/npz/urban-tracker-stmarc-pedestrian-test.npz"

analysis_dir="/users/ahjiang/src/mainstream-analysis/output/bb/raw/"
plot_prefix=$analysis_dir"plots/urban-tracker/stmarc/pedestrian-pr"
output_image_dir=$analysis_dir"images/urban-tracker/stmarc"
result_path=$analysis_dir"inference/urban-tracker/stmarc/urban-tracker-stmarc-pedestrian-results"

step=5
start=5
end=5
ns=5

trial_start=0
trial_end=0
trial_step=1

for i in `seq $start $step $end`;
do
    for j in `seq $trial_start $trial_step $trial_end`;
    do
        model_path=$model_prefix"-"$i"fr-trial"$j".h5"
        plot_path=$plot_prefix"-"$i".pdf"
        output_path=$output_image_dir"/"$i
        mkdir $output_path
        python -u src/inference/inference_yad2k.py -ns $ns \
                                                   --mode 1 \
                                                   -c $labels \
                                                   --identifier $i \
                                                   -p $plot_path \
                                                   -o $output_path \
                                                   -r $result_path \
                                                   --model_path $model_path \
                                                   -t $input
        echo "Results written to: "$result_path
    done
done
