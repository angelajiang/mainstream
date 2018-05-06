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
@pytest.mark.parametrize("scheduler_ref,schedulers_test,num_apps,check_schedules", [
    ("exhaustive", ["hifi", "stems", "stems_cpp"], 3, False),
])
def test_optimality(scheduler_ref, schedulers_test, num_apps, check_schedules):
    idx = scheduler_ref + "_vs_" + ",".join(schedulers_test)
    output_dir, schedules_dir = get_dir(idx)
    subprocess.check_call("test/gen_setups.sh {} {} {} {}".format(idx,
                                                                  num_apps,
                                                                  output_dir,
                                                                  "config/scheduler/setup_fast.v1"), shell=True)

    all_f1s = {}
    all_schedules = {}

    for scheduler in [scheduler_ref] + schedulers_test:
        subprocess.check_call("test/run_scheduler_only.sh {} {}".format(scheduler,
                                                                        output_dir), shell=True)
        f1s = []
        schedules = []
        filename = os.path.join(schedules_dir, scheduler + ".mainstream.sim.100.debug.v1")
        with open(filename, "r") as f:
            for line in f:
                vals = line.split(',')
                f1s.append(round(float(vals[2]), 3))
                num_apps = int(vals[1])
                schedules.append(vals[3:3 + num_apps * 2])
        all_f1s[scheduler] = f1s
        all_schedules[scheduler] = schedules

    for scheduler in schedulers_test:
        assert all_f1s[scheduler] == all_f1s[scheduler_ref]
        if check_schedules:
            assert all_schedules[scheduler] == all_schedules[scheduler_ref]

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
