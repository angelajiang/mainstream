#!/bin/bash
for i in {1..8}
do
    pypy src/scheduler/run_scheduler_sim_permute.py $i log/scheduler-permute-min-$i.csv --agg min >> log/simlogs/scheduler-permute-min-$i.out &
done
