#!/bin/bash
set -e
bash gen_setups.sh $1 $2 $3
bash run_scheduler_only.sh $1 $3
