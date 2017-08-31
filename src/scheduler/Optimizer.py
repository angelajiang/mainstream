import csv
from gurobipy import *
sys.path.append('src/scheduler')
import scheduler_util
import numpy as np
import os
import sys


def optimize(apps, stream_fps):
    ## Optimizes for minimizing false negative rate
    ## Sets num_frozen_list and target_fps_list

    unique_branchpoints = set()
    for app in apps:
        for branchpoint in app["accuracies"]:
            unique_branchpoints.add(branchpoint)
    branchpoints = list(sorted(unique_branchpoints))

    try:
        # Create a new model
        m = Model("min-false-neg")
        m.setParam('OutputFlag', False )
        m.params.OptimalityTol = 1e-2
        m.params.timeLimit = 60.0

        # Create num frozen index variables (Fs)
        # Create throughput variables (Ts)
        Fs = []
        Ts = []
        for app in apps:
            aid = str(app["app_id"])
            f = m.addVar(vtype=GRB.INTEGER, ub=len(branchpoints)-1, name="f"+aid)
            t = m.addVar(vtype=GRB.INTEGER, ub=stream_fps, name="t"+aid)
            Fs.append(f)
            Ts.append(t)

        # Set objective
        expr = LinExpr()
        for app, f, t in zip(apps, Fs, Ts):
            expr.add(t, 2)
            expr.add(f, 2)

        m.setObjective(expr, GRB.MAXIMIZE)

        # Add constraints
        #m.addConstr(event_length_ms / float(1000) * t >= 1, "c1")

        m.optimize()

        # Print schedule
        for app, f, t in zip(apps, Fs, Ts):
            print f.VarName + ":", f.X
            print t.VarName + ":", t.X
            num_frozen = branchpoints[int(f.X)]
            accuracy = app["accuracies"][num_frozen]
            false_neg_rate = scheduler_util.get_false_neg_rate(
                                              accuracy,
                                              app["event_length_ms"],
                                              stream_fps,
                                              t.X)
            print "False neg rate: ", round(false_neg_rate, 2)

        return 1

    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))
        return -1

    print stream_fps

    return [87, 87, 87], [2, 4, 4]

if __name__ == "__main__":

    apps = [
            {"app_id": 0,
             "model_path": "app1_model.pb",
             "event_length_ms": 50,
             "accuracies": {1: 1,
                            10: 0.8,
                            21: 0.6,
                            30: 0.6,
                            40: 0.2
                           }
             },
            {"app_id":1,
             "model_path": "app2_model.pb",
             "event_length_ms": 50,
             "accuracies": {1: 1,
                            10: 1,
                            21: 0.8,
                            30: 0.6,
                            40: 0.2
                           }
             }
           ]

    optimize(apps, 30)
