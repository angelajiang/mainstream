import os
import shutil
import subprocess
import pytest

@pytest.mark.unit
def test_hifi_scheduler():
    output_dir = os.path.join("test", "tmp")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    schedules_dir = os.path.join(output_dir, "schedules")
    hifi_file = os.path.join(schedules_dir, "hifi.sim.debug.v0")
    exhaustive_file = os.path.join(schedules_dir, "exhaustive.debug.v0")

    subprocess.call("test/hifi_vs_exhaustive.sh", shell=True)

    hifi_f1s = []
    with open(hifi_file, "r") as f:
        for line in f:
            vals = line.split(',')
            metric = round(float(vals[1]), 2)
            hifi_f1s.append(metric)

    exhaustive_f1s = []
    with open(exhaustive_file, "r") as f:
        for line in f:
            vals = line.split(',')
            metric = round(float(vals[1]), 2)
            exhaustive_f1s.append(metric)

    print hifi_f1s
    print exhaustive_f1s
    assert hifi_f1s == exhaustive_f1s

    shutil.rmtree(output_dir)

