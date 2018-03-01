#!/bin/bash
sem -j+0 python src/scheduler/run_scheduler_simulator.py 10 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-cars-500 -m f1 --datasets cars > log/distributed/inception-f1-cars-500-mainstream-simulator.out
sem -j+0 python src/scheduler/run_scheduler_simulator.py 10 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-cats-500 -m f1 --datasets cats > log/distributed/inception-f1-cats-500-mainstream-simulator.out
sem -j+0 python src/scheduler/run_scheduler_simulator.py 10 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-pedestrian-500 -m f1 --datasets pedestrian > log/distributed/inception-f1-pedestrian-500-mainstream-simulator.out
sem -j+0 python src/scheduler/run_scheduler_simulator.py 10 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-train-500 -m f1 --datasets train > log/distributed/inception-f1-train-500-mainstream-simulator.out
sem -j+0 python src/scheduler/run_scheduler_simulator.py 10 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-flowers-500 -m f1 --datasets flowers > log/distributed/inception-f1-flowers-500-mainstream-simulator.out
sem --wait
