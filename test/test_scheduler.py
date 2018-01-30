import sys
sys.path.append('src/scheduler')
import Schedule
import Scheduler
import pprint as pp
import pytest

video_desc = {"stream_fps": 5}
model_desc = {"total_layers": 41,
              "channels": 3,
              "height": 299,
              "width": 299,
              "layer_latencies": [1] * 41,
              "frozen_layer_names": {1: "input",
                                     10: "conv1",
                                     21: "conv2",
                                     30: "pool",
                                     40: "fc",
                                     41: "softmax"}}

apps = [ 
        {"app_id": 1,
        "model_path": {
            0: "app1_model.pb",
            10: "app1_model.pb",
            21: "app1_model.pb",
            30: "app1_model.pb",
            40: "app1_model.pb"
        },
        "event_length_ms": 500,
        "correlation": 0,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        },
        {"app_id": 2,
        "model_path": {
            0: "app2_model.pb",
            10: "app2_model.pb",
            21: "app2_model.pb",
            30: "app2_model.pb",
            40: "app2_model.pb"
        },
        "event_length_ms": 500,
        "correlation": 0,
        "accuracies": {1: 1,
                       10: 1,
                       21: 0.8,
                       30: 0.6,
                       40: 0.2
                      }
        },
        {"app_id": 3,
        "model_path": {
            0: "app3_model.pb",
            10: "app3_model.pb",
            21: "app3_model.pb",
            30: "app3_model.pb",
            40: "app3_model.pb"
        },
        "event_length_ms": 500,
        "correlation": 0,
        "accuracies": {1: 1,
                       10: 1,
                       21: 1,
                       30: 0.8,
                       40: 0.6
                      }
        }]

@pytest.mark.unit
def test_optimize_parameters():

    three_apps = apps[:3]       # Decrease to three apps so we can brute force
    s = Scheduler.Scheduler("fnr", three_apps, video_desc, model_desc, 0)

    # Quickly get reference values with s.get_parameter_options()
    '''
    schedules, metrics, costs = s.get_parameter_options()
    for sched, m, c in zip(schedules, metrics, costs):
        print "----------------------------"
        print "False neg:", m, ",", "Cost:", c
        for unit in sched:
            print unit.app_id, ":", unit.target_fps, ",", unit.num_frozen
            '''

    # Heuristic does not achieve lowest possible FNR
    metric = round(s.optimize_parameters(489), 4)
    assert metric > 0.0
    metric = round(s.optimize_parameters(408), 4)
    assert metric > 0.0333
    metric = round(s.optimize_parameters(405), 4)
    assert metric > 0.0445
    metric = round(s.optimize_parameters(385), 4)
    assert metric > 0.0581
    metric = round(s.optimize_parameters(377), 4)
    assert metric > 0.0667
    metric = round(s.optimize_parameters(365), 4)
    assert metric > 0.0915

@pytest.mark.unit
def test_make_streamer_schedule():
    ref_schedule = \
            [{"net_id": 0,
              "app_id": -1,
              "parent_id": -1,
              "input_layer": "input",
              "output_layer": "conv1",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 8,
              "shared": True,
              "model_path": "app1_model.pb"
             },
             {"net_id": 1,
              "app_id": 1,
              "parent_id": 0,
              "input_layer": "conv1",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 2,
              "shared": False,
              "model_path": "app1_model.pb"
              },
             {"net_id": 2,
              "app_id": -1,
              "parent_id": 0,
              "input_layer": "conv1",
              "output_layer": "pool",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 8,
              "shared": True,
              "model_path": "app2_model.pb"
              },
             {"net_id": 3,
              "app_id": 2,
              "parent_id": 2,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 4,
              "shared": False,
              "model_path": "app2_model.pb"
              },
             {"net_id": 4,
              "app_id": 3,
              "parent_id": 2,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 8,
              "shared": False,
              "model_path": "app3_model.pb"
              }
              ]

    s = Scheduler.Scheduler("fnr", apps, video_desc, model_desc, 0)

    s.num_frozen_list = [10, 30, 40]
    s.target_fps_list = [2, 4, 8]

    schedule = s.make_streamer_schedule()

    assert ref_schedule == schedule

