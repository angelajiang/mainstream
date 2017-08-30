import csv
from gurobipy import *
import numpy as np
import os
import sys

'''
apps = [{"model_path": "app1_model.pb",
        "event_length_ms": 10,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        }]
'''

def optimize(apps, stream_fps):
    ## Optimizes for minimizing false negative rate
    ## Sets num_frozen_list and target_fps_list
    try:
        # Create a new model
        m = Model("min-false-neg")
        m.setParam('OutputFlag', False )
        m.params.OptimalityTol = 1e-2
        m.params.timeLimit = 60.0

        # Create variables
        X = m.addVar(vtype=GRB.INTEGER, obj=1.0, name="x")

        # Set objective
        m.setObjective(X,  GRB.MAXIMIZE)

        # Add constraints
        m.addConstr(X <= 1, "c1")

        m.optimize()

        print X.x

        return 1

    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
        return -1

    except AttributeError:
        print('AttributeError')
        return -1

    print stream_fps

    return [87, 87, 87], [2, 4, 4]

if __name__ == "__main__":

    apps = [
            {"model_path": "app1_model.pb",
            "event_length_ms": 10,
            "accuracies": {1: 1,
                           10: 0.8,
                           21: 0.6,
                           30: 0.6,
                           40: 0.2
                          }
            },
            {"model_path": "app2_model.pb",
            "event_length_ms": 10,
            "accuracies": {1: 1,
                           10: 1,
                           21: 0.8,
                           30: 0.6,
                           40: 0.2
                          }
            }
           ]

    optimize(apps, 30)
