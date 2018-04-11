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
    if not os.path.exists(schedules_dir):
        os.makedirs(schedules_dir)
    other_file = os.path.join(schedules_dir, scheduler_type + ".sim.debug.v0")
    exhaustive_file = os.path.join(schedules_dir, "exhaustive.sim.debug.v0")

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


@pytest.mark.unit
@pytest.mark.parametrize("scheduler_type,num_apps_range", [
    ("hifi", 5),
    ("stems", 5),
    ("exhaustive", 3),
    ("stems_cpp", 5),
])
def test_regression(regtest, scheduler_type, num_apps_range):
    output_dir = os.path.join("test", "tmp", scheduler_type)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    schedules_dir = os.path.join(output_dir, "schedules")
    if not os.path.exists(schedules_dir):
        os.makedirs(schedules_dir)
    other_file = os.path.join(schedules_dir, scheduler_type + ".sim.debug.v0")

    subprocess.check_call("test/run_scheduler_with_setups.sh {} {}".format(scheduler_type, num_apps_range), shell=True)

    with open(other_file) as f:
        for line in f:
            line = line.split(",")[:-1]
            regtest.write(",".join(line) + "\n")

    shutil.rmtree(output_dir)
