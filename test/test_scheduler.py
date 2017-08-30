import sys
sys.path.append('src/scheduler')
import dynamic_scheduler
import pprint as pp
import pytest

model_desc = {"total_layers": 41,
              "channels": 3,
              "height": 299,
              "width": 299,
              "frozen_layer_names": {1: "input",
                                     10: "conv1",
                                     21: "conv2",
                                     30: "pool",
                                     40: "fc",
                                     41: "softmax"}}

app1 = {"model_path": "app1_model.pb",
        "within_frames_slo": 10,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        }
app2 = {"model_path": "app2_model.pb",
        "within_frames_slo": 10,
        "accuracies": {1: 1,
                       10: 1,
                       21: 0.8,
                       30: 0.6,
                       40: 0.2
                      }
        }
app3 = {"model_path": "app3_model.pb",
        "within_frames_slo": 10,
        "accuracies": {1: 1,
                       10: 1,
                       21: 1,
                       30: 0.8,
                       40: 0.6
                      }
        }
app4 = {"model_path": "app4_model.pb",
        "within_frames_slo": 10,
        "accuracies": {1: 1,
                       10: 1,
                       21: 1,
                       30: 0.9,
                       40: 0.6
                      }
        }

@pytest.mark.unit
def test_get_num_frozen_list():
    #get_num_frozen_list(apps, cur_num_frozen_list):
    apps = [app1, app2, app3, app4]

    ref_num_frozen_list_0 = [1, 10, 21, 21] # Tests initialization
    ref_num_frozen_list_1 = [1, 10, 21, 30] # Tests basic functionality
    ref_num_frozen_list_2 = [1, 21, 21, 30] # Tests tie-breaker

    # Test num_frozen_list initialization
    cur_num_frozen_list = \
        dynamic_scheduler.get_num_frozen_list(apps, [])
    assert ref_num_frozen_list_0 == cur_num_frozen_list

    cur_num_frozen_list = \
        dynamic_scheduler.get_num_frozen_list(apps, cur_num_frozen_list)
    assert ref_num_frozen_list_1 == cur_num_frozen_list

    cur_num_frozen_list = \
        dynamic_scheduler.get_num_frozen_list(apps, cur_num_frozen_list)
    assert ref_num_frozen_list_2 == cur_num_frozen_list

@pytest.mark.unit
def test_scheduler():
    apps = [app1, app2, app3, app4]
    num_frozen_list = [10, 30, 30, 40]
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
              "output_layer": "pool",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": True,
              "model_path": "app2_model.pb"
              },
             {"net_id": 3,
              "parent_id": 2,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app2_model.pb"
              },
             {"net_id": 4,
              "parent_id": 2,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app3_model.pb"
              },
             {"net_id": 5,
              "parent_id": 2,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "shared": False,
              "model_path": "app4_model.pb"
              }]

    schedule = dynamic_scheduler.schedule(apps, num_frozen_list, model_desc)
    assert ref_schedule == schedule

