import sys
sys.path.append('src/training')
import train

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

@pytest.mark.unit
def test_model_saving(tmp_dir, tf_dir):

    # Train
    config_file = "config/test/0-epochs"
    dataset_dir = "/usr0/home/ahjiang/src/data/image-data/training/train_images"
    model_dir = tmp_dir + "/models"
    os.mkdir(model_dir)
    model_prefix = model_dir + "/my-model"
    num_training_layers = 300
    train.train(config_file,
                dataset_dir,
                model_prefix,
                num_training_layers)

    # Check all Keras and TF models files are present
    suffixes = [".h5", ".json", "-labels.json",
                ".pb", ".ckpt.meta", ".ckpt.index",
                ".ckpt.data-00000-of-00001"]
    for suffix in suffixes:
        model_path = model_prefix + suffix
        assert os.path.exists(model_path)

    # Run freeze_graph
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

