import sys
sys.path.append('src/scheduler')
import scheduler
import pprint as pp
import pytest

@pytest.mark.unit
def test_scheduler():
    # Set up data
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
    apps = [app1, app2, app3, app4]
    threshold = 0.2
    final_layer = 45

    ref_num_frozen = [10, 20, 30, 30]
    ref_schedule = \
            [{"net_id": 0,
              "parent_id": -1,
              "start": 1,
              "end": 10,
              "model_path": "app1_model.pb"
             },
             {"net_id": 1,
              "parent_id": 0,
              "start": 11,
              "end": 45,
              "model_path": "app1_model.pb"
              },
             {"net_id": 2,
              "parent_id": 0,
              "start": 11,
              "end": 20,
              "model_path": "app2_model.pb"
              },
             {"net_id": 3,
              "parent_id": 2,
              "start": 21,
              "end": 45,
              "model_path": "app2_model.pb"
              },
             {"net_id": 4,
              "parent_id": 2,
              "start": 21,
              "end": 45,
              "model_path": "app3_model.pb"
              },
             {"net_id": 5,
              "parent_id": 2,
              "start": 21,
              "end": 45,
              "model_path": "app4_model.pb"
              }]

    # Test get_num_frozen is accurate
    for app, ref in zip(apps, ref_num_frozen):
        accs = app["accuracies"]
        num_frozen = scheduler.get_num_frozen(accs, threshold)
        assert num_frozen == ref

    # Test scheduler is accurate
    schedule = scheduler.schedule(apps, threshold, final_layer)
    assert ref_schedule ==  schedule
