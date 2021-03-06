import os
import pytest
import shutil
from _pytest.runner import runtestprotocol

def pytest_addoption(parser):
    parser.addoption("--data_dir", action="store", default="~/")
    parser.addoption("--config", action="store", default="~/")

def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    data_val = metafunc.config.option.data_dir
    if 'data_dir_fixture' in metafunc.fixturenames and data_val is not None:
        metafunc.parametrize("data_dir_fixture", [data_val], scope="session")
    config_val = metafunc.config.option.config
    if 'config_fixture' in metafunc.fixturenames and config_val is not None:
        metafunc.parametrize("config_fixture", [config_val], scope="session")

def pytest_runtest_protocol(item, nextitem):
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            print '\n%s --- %s' % (item.name, report.outcome)
    return True

# Make temporary test directory
@pytest.fixture(scope="session")
def tmp_dir_fixture(request):
    os.mkdir("test-dir")
    def teardown():
        shutil.rmtree("test-dir")
    request.addfinalizer(teardown)
    return "test-dir"


