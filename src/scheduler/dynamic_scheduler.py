import sys
sys.path.append('src/scheduler')
import scheduler


def get_relative_accuracies(apps, num_frozen_list):
    relative_accuracies = []
    for app, num_frozen in zip(apps, num_frozen_list):
        max_acc = max(app["accuracies"].values())
        cur_acc = app["accuracies"][num_frozen]
        rel_acc = (max_acc - cur_acc) / max_acc
        relative_accuracies.append(rel_acc)
    return relative_accuracies

def schedule(apps, num_frozen_list, model_desc):
    return scheduler.schedule(apps, num_frozen_list, model_desc)
