#!/bin/bash
for i in {1..10}
do
   pypy src/scheduler/run_scheduler_sim_permute.py $i log/sched-sim-permute-all-$i.csv --curves all2 >> log/simlogs/sched-sim-permute-all-$i.out &
done
