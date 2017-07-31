import sys
sys.path.append('src/scheduler')
import scheduler
import pprint as pp
import pytest

model_desc = {"total_layers": 41,
              "channels": 3,
              "height": 299,
              "width": 299,
              "frozen_layer_names": {1: "input",
                                     10: "conv1",
                                     20: "conv2",
                                     30: "pool",
                                     40: "fc",
                                     41: "softmax"}}

app1 = {"model_path": "app1_model.pb",
        "accuracies": {1: 1,
                       10: 0.8,
                       20: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        }
app2 = {"model_path": "app2_model.pb",
        "accuracies": {1: 1,
                       10: 1,
                       20: 0.8,
                       30: 0.6,
                       40: 0.2
                      }
        }
app3 = {"model_path": "app3_model.pb",
        "accuracies": {1: 1,
                       10: 1,
                       20: 1,
                       30: 0.8,
                       40: 0.6
                      }
        }
app4 = {"model_path": "app4_model.pb",
        "accuracies": {1: 1,
                       10: 1,
                       20: 1,
                       30: 0.8,
                       40: 0.6
                      }
        }

@pytest.mark.unit
def test_share_everything():

    apps = [app1, app2]
    threshold = 1

    ref_num_frozen = [40, 40]
    ref_schedule = \
            [{"net_id": 0,
              "parent_id": -1,
              "input_layer": "input",
              "output_layer": "fc",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": True,
              "model_path": "app1_model.pb"
             },
             {"net_id": 1,
              "parent_id": 0,
              "input_layer": "fc",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app1_model.pb"
              },
             {"net_id": 2,
              "parent_id": 0,
              "input_layer": "fc",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app2_model.pb"
              }]

    # Test get_num_frozen is accurate
    for app, ref in zip(apps, ref_num_frozen):
        accs = app["accuracies"]
        num_frozen = scheduler.get_num_frozen(accs, threshold)
        assert num_frozen == ref

    # Test scheduler is accurate
    schedule = scheduler.schedule(apps, threshold, model_desc)
    assert ref_schedule ==  schedule

@pytest.mark.unit
def test_scheduler():
    # Set up data

    apps = [app1, app2, app3, app4]
    threshold = 0.2

    ref_num_frozen = [10, 20, 30, 30]
    ref_schedule = \
            [{"net_id": 0,
              "parent_id": -1,
              "input_layer": "input",
              "output_layer": "conv1",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": True,
              "model_path": "app1_model.pb"
             },
             {"net_id": 1,
              "parent_id": 0,
              "input_layer": "conv1",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app1_model.pb"
              },
             {"net_id": 2,
              "parent_id": 0,
              "input_layer": "conv1",
              "output_layer": "conv2",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": True,
              "model_path": "app2_model.pb"
              },
             {"net_id": 3,
              "parent_id": 2,
              "input_layer": "conv2",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app2_model.pb"
              },
             {"net_id": 4,
              "parent_id": 2,
              "input_layer": "conv2",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app3_model.pb"
              },
             {"net_id": 5,
              "parent_id": 2,
              "input_layer": "conv2",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app4_model.pb"
              }]

    # Test get_num_frozen is accurate
    for app, ref in zip(apps, ref_num_frozen):
        accs = app["accuracies"]
        num_frozen = scheduler.get_num_frozen(accs, threshold)
        assert num_frozen == ref

    # Test scheduler is accurate
    schedule = scheduler.schedule(apps, threshold, model_desc)
    assert ref_schedule ==  schedule
