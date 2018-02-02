#!/bin/bash
for i in {1..8}
do
   pypy src/scheduler/run_scheduler_sim_permute.py $i log/sched-sim-permute-all-$i.csv --curves all >> log/simlogs/sched-sim-permute-all-$i.out &
done
