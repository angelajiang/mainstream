#!/bin/bash
for i in {1..8}
do
   pypy src/scheduler/run_scheduler_sim_permute.py $i log/sched-sim-permute-$i.csv >> log/simlogs/sched-sim-permute-$i.out &
done
