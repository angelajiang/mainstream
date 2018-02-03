for i in 1 2 3; do
    for j in f1 fnr fpr; do
        sem -j+0 python src/scheduler/run_scheduler_simulator.py 20 $i ../mainstream-analysis/output/streamer/scheduler/atc/$j/$j-train-500 -m $j
    done
done
sem --wait
