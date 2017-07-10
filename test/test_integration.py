import sys
sys.path.append('src/training')
sys.path.append('src/inference')
import train
import inference_pb
import inference_h5

import os
import pytest
import shutil
import subprocess


@pytest.fixture
def tmp_dir(request):
    os.mkdir("test-dir")
    def teardown():
        shutil.rmtree("test-dir")
    request.addfinalizer(teardown)
    return "test-dir"

# Test that h5 and pb files are saved correctly by showing that they provide
# the same inference results

def run_model_saving_test(tmp_dir, data_dir, tf_dir, config_file):

    ## Train
    model_dir = tmp_dir + "/models"
    os.mkdir(model_dir)
    model_prefix = model_dir + "/my-model"
    num_training_layers = 300
    train.train(config_file,
                data_dir,
                model_prefix,
                num_training_layers)

    ## Check all Keras and TF models files are present
    suffixes = [".h5", ".json", "-labels.json",
                ".pb", ".ckpt.meta", ".ckpt.index",
                ".ckpt.data-00000-of-00001"]
    for suffix in suffixes:
        model_path = model_prefix + suffix
        assert os.path.exists(model_path)

    ## Run freeze_graph
    freeze_path = tf_dir + "/bazel-bin/tensorflow/python/tools/freeze_graph"
    frozen_graph_path = model_prefix + "-frozen.pb"
    # Check that freeze_graph binary has been built
    assert os.path.exists(freeze_path)
    args = (freeze_path,
            "--input_binary", "True",
            "--output_node_names", "dense_2/Softmax",
            "--input_graph", model_prefix + ".pb",
            "--input_checkpoint", model_prefix + ".ckpt",
            "--output_graph", frozen_graph_path)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    # Check that frozen_graph has been created
    assert os.path.exists(frozen_graph_path)

    ## Run inference
    pb_out = inference_pb.predict(frozen_graph_path, data_dir)
    h5_out = inference_h5.predict(model_prefix, data_dir)

    ## Compare inference output
    for h5_val, pb_val in zip(h5_out, pb_out):
        print h5_val[0], h5_val[1], ",",  pb_val[0], pb_val[1]
        assert round(h5_val[0], 1) == round(pb_val[0], 1)
        assert round(h5_val[1], 1) == round(pb_val[1], 1)

@pytest.mark.unit
def test_model_saving_no_training(tmp_dir, data_dir, tf_dir):
    config_file = "config/test/0-epochs"
    run_model_saving_test(tmp_dir, data_dir, tf_dir, config_file)

@pytest.mark.unit
def test_model_saving_training(tmp_dir, data_dir, tf_dir):
    config_file = "config/test/1-epoch"
    run_model_saving_test(tmp_dir, data_dir, tf_dir, config_file)

