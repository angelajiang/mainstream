import sys
sys.path.append('src/training')
sys.path.append('src/inference')
sys.path.append('src/util')
import Data
import train
import inference_pb
import inference_h5
import freeze

import os
import pytest
import subprocess
import uuid

# Fixtures perform model saving so it only occurs once per session

@pytest.fixture(scope="session")
def models_fixture(tmp_dir_fixture, data_dir_fixture, config_fixture):
    pb_model_path, h5_model_path = \
        save_models(tmp_dir_fixture, data_dir_fixture, config_fixture)
    return pb_model_path, h5_model_path

@pytest.fixture(scope="session")
def dataset_fixture(data_dir_fixture):
    return Data.Data(data_dir_fixture, None, 299)

def save_models(tmp_dir, data_dir, config_file):

    ## Train
    model_dir = tmp_dir + "/models"
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    model_prefix = model_dir + "/my-model-" + str(uuid.uuid4())[:8]
    num_frozen = 310
    train.train(config_file,
                data_dir,
                model_prefix,
                num_frozen)

    ## Check all Keras and TF models files are present
    suffixes = [".h5", ".json", "-labels.json",
                ".pb", ".ckpt.meta", ".ckpt.index",
                ".ckpt.data-00000-of-00001"]
    for suffix in suffixes:
        model_path = model_prefix + suffix
        assert os.path.exists(model_path)

    ## Run freeze_graph
    freeze.freeze(model_prefix)
    frozen_graph_path = model_prefix + "-frozen.pb"
    assert os.path.exists(frozen_graph_path)

    return frozen_graph_path, model_prefix

# Test that h5 and pb files are saved correctly by showing that they provide
# the same inference results

def compare_inference_output(models, test_dataset):
    pb_model_path = models[0]
    h5_model_path = models[1]

    ## Run inference
    pb_out = inference_pb.predict_with_dataset(pb_model_path, test_dataset)
    h5_out = inference_h5.predict_with_dataset(h5_model_path, test_dataset)

    ## Compare inference output
    for h5_val, pb_val in zip(h5_out, pb_out):
        assert round(h5_val[0], 2) == round(pb_val[0], 2)
        assert round(h5_val[1], 2) == round(pb_val[1], 2)

@pytest.mark.unit
def test_inference(models_fixture, dataset_fixture):
    compare_inference_output(models_fixture, dataset_fixture)

