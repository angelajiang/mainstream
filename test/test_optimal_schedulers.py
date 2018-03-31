import os
import shutil
import subprocess
import pytest

@pytest.mark.unit
@pytest.mark.parametrize("scheduler_type", ["hifi", "stems"])
def test_optimality(scheduler_type):
    output_dir = os.path.join("test", "tmp", scheduler_type)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    schedules_dir = os.path.join(output_dir, "schedules")
    other_file = os.path.join(schedules_dir, scheduler_type + ".sim.debug.v0")
    exhaustive_file = os.path.join(schedules_dir, "exhaustive.debug.v0")

    subprocess.check_call("test/exhaustive_vs_x_scheduler.sh " + scheduler_type, shell=True)

    other_f1s = []
    with open(other_file, "r") as f:
        for line in f:
            vals = line.split(',')
            metric = round(float(vals[1]), 2)
            other_f1s.append(metric)

    exhaustive_f1s = []
    with open(exhaustive_file, "r") as f:
        for line in f:
            vals = line.split(',')
            metric = round(float(vals[1]), 2)
            exhaustive_f1s.append(metric)

    assert other_f1s == exhaustive_f1s

    shutil.rmtree(output_dir)
