import sys
sys.path.append('src/scheduler/types')
import Schedule
import Scheduler
import pprint as pp
import pytest

video_desc = {"stream_fps": 15}
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
        "event_length_ms": 5000,
        "event_frequency": 0.3,
        "correlation_coefficient": 0.1,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      },
        "prob_tnrs": {1: 0.1,
                      10: 0.1,
                      21: 0.1,
                      30: 0.1,
                      40: 0.1
                      },
        },
        {"app_id": 2,
        "model_path": {
            0: "app2_model.pb",
            10: "app2_model.pb",
            21: "app2_model.pb",
            30: "app2_model.pb",
            40: "app2_model.pb"
        },
        "event_length_ms": 5000,
        "event_frequency": 0.3,
        "correlation_coefficient": 0.1,
        "accuracies": {1: 1,
                       10: 1,
                       21: 0.8,
                       30: 0.6,
                       40: 0.1
                      },
        "prob_tnrs": {1: 0.1,
                      10: 0.1,
                      21: 0.1,
                      30: 0.1,
                      40: 0.1
                      },
        },
        {"app_id": 3,
        "model_path": {
            0: "app3_model.pb",
            10: "app3_model.pb",
            21: "app3_model.pb",
            30: "app3_model.pb",
            40: "app3_model.pb"
        },
        "event_length_ms": 5000,
        "event_frequency": 0.3,
        "correlation_coefficient": 0.1,
        "accuracies": {1: 1,
                       10: 1,
                       21: 1,
                       30: 0.8,
                       40: 0.6
                      },
        "prob_tnrs": {1: 0.1,
                      10: 0.1,
                      21: 0.1,
                      30: 0.1,
                      40: 0.1
                      },
        },
        {"app_id": 4,
        "model_path": {
            0: "app4_model.pb",
            10: "app4_model.pb",
            21: "app4_model.pb",
            30: "app4_model.pb",
            40: "app4_model.pb"
        },
        "event_length_ms": 5000,
        "event_frequency": 0.3,
        "correlation_coefficient": 0.1,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.7,
                       30: 0.7,
                       40: 0.6
                      },
        "prob_tnrs": {1: 0.1,
                      10: 0.1,
                      21: 0.1,
                      30: 0.1,
                      40: 0.1
                      },
        }
        ]

@pytest.mark.unit
@pytest.mark.filterwarnings('ignore:Not enough bites')
def test_optimize_parameters():

    three_apps = apps[:3]       # Decrease to three apps so we can brute force
    s = Scheduler.Scheduler("f1", three_apps, video_desc, model_desc)

    # Quickly get reference values with s.get_parameter_options()
    '''
    schedules, metrics, costs = s.get_parameter_options()
    for sched, m, c in zip(schedules, metrics, costs):
        print "----------------------------"
        print "1- F1:", m, ",", "Cost:", c
        for unit in sched:
            print unit.app_id, ":", unit.target_fps, ",", unit.num_frozen
    '''

    # Heuristic does not achieve highest possible F1
    # Best case metric: 0.129 _should_ be achievable with cost: 242
    metric = round(s.optimize_parameters(400), 4)
    print metric
    assert metric == 0.129

@pytest.mark.unit
def test_make_streamer_schedule():
    ref_schedule = \
            [
            {"net_id": 0,
              "app_id": 4,
              "parent_id": -1,
              "input_layer": "input",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 8,
              "shared": False,
              "model_path": "app4_model.pb"
             },
            {"net_id": 1,
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
             {"net_id": 2,
              "app_id": 1,
              "parent_id": 1,
              "input_layer": "conv1",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 2,
              "shared": False,
              "model_path": "app1_model.pb"
              },
             {"net_id": 3,
              "app_id": -1,
              "parent_id": 1,
              "input_layer": "conv1",
              "output_layer": "pool",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 8,
              "shared": True,
              "model_path": "app2_model.pb"
              },
             {"net_id": 4,
              "app_id": 2,
              "parent_id": 3,
              "input_layer": "pool",
              "output_layer": "softmax",
              "channels": 3,
              "height": 299,
              "width": 299,
              "target_fps": 4,
              "shared": False,
              "model_path": "app2_model.pb"
              },
             {"net_id": 5,
              "app_id": 3,
              "parent_id": 3,
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

    s = Scheduler.Scheduler("fnr", apps, video_desc, model_desc)

    s.num_frozen_list = [10, 30, 40, 0]
    s.target_fps_list = [2, 4, 8, 8]

    schedule = s.make_streamer_schedule()

    assert ref_schedule == schedule

