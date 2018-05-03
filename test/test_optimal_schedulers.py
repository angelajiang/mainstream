import uuid
import random
import os
import shutil
import subprocess
import pytest

random.seed(1337)


def get_dir(idx):
    output_dir = os.path.join("test", "tmp", idx + "-" + str(uuid.uuid4())[:8])
    schedules_dir = os.path.join(output_dir, "schedules")
    return output_dir, schedules_dir


@pytest.mark.unit
@pytest.mark.parametrize("scheduler_type", ["hifi", "stems", "stems_cpp"])
def test_optimality(scheduler_type):
    idx = "exhaustive" + "_vs_" + scheduler_type
    output_dir, schedules_dir = get_dir(idx)
    other_file = os.path.join(schedules_dir, scheduler_type + ".mainstream.sim.100.debug.v1")
    exhaustive_file = os.path.join(schedules_dir, "exhaustive.mainstream.sim.100.debug.v1")

    subprocess.check_call("test/gen_setups.sh {} {} {} {}".format(idx,
                                                                  3,
                                                                  output_dir,
                                                                  "config/scheduler/setup_fast.v1"), shell=True)
    subprocess.check_call("test/run_scheduler_only.sh {} {}".format("exhaustive",
                                                                    output_dir), shell=True)
    subprocess.check_call("test/run_scheduler_only.sh {} {}".format(scheduler_type,
                                                                    output_dir), shell=True)

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
    output_dir, schedules_dir = get_dir(scheduler_type)
    other_file = os.path.join(schedules_dir, scheduler_type + ".mainstream.sim.100.debug.v1")

    subprocess.check_call("test/gen_setups.sh {} {} {}".format(scheduler_type,
                                                               num_apps_range,
                                                               output_dir), shell=True)
    subprocess.check_call("test/run_scheduler_only.sh {} {}".format(scheduler_type,
                                                                    output_dir), shell=True)

    with open(other_file) as f:
        for line in f:
            line = line.split(",")[:-1]
            regtest.write(",".join(line) + "\n")

    shutil.rmtree(output_dir)
