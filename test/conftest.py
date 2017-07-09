
def pytest_addoption(parser):
    parser.addoption("--tf_dir", action="store", default="~/tensorflow/")

def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.tf_dir
    if 'tf_dir' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("tf_dir", [option_value])

