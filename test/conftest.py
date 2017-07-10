
def pytest_addoption(parser):
    parser.addoption("--tf_dir", action="store", default="~/tensorflow/")
    parser.addoption("--data_dir", action="store", default="~/")

def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    tf_val = metafunc.config.option.tf_dir
    if 'tf_dir' in metafunc.fixturenames and tf_val is not None:
        metafunc.parametrize("tf_dir", [tf_val])
    data_val = metafunc.config.option.data_dir
    if 'data_dir' in metafunc.fixturenames and data_val is not None:
        metafunc.parametrize("data_dir", [data_val])

