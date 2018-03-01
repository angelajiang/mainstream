#!/bin/bash
sem -j+0 python src/scheduler/run_scheduler_simulator.py 50 ../mainstream-analysis/output/streamer/scheduler/distributed/f1/inception/f1-cars-cats-pedestrian-train-flowers-500 -m f1 --datasets cars cats pedestrian train flowers > log/distributed/inception-f1-cars-cats-pedestrian-train-flowers-500-mainstream-simulator.out
sem --wait
