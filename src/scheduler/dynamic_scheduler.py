import sys
sys.path.append('src/scheduler')
import scheduler


def get_relative_accuracy(app, num_frozen):
    max_acc = max(app["accuracies"].values())
    cur_acc = app["accuracies"][num_frozen]
    rel_acc = (max_acc - cur_acc) / max_acc
    return rel_acc

def get_next_frozen_layer(app, num_frozen):
# Want more layers frozen
    for layers in sorted(app["accuracies"].keys()):
        if layers > num_frozen:
            return layers
    return num_frozen # Already at max

def schedule(apps, num_frozen_list, model_desc):
    return scheduler.schedule(apps, num_frozen_list, model_desc)

def get_num_frozen_list(apps, cur_num_frozen_list):
# Change at most one frozen layer to share more
# Returns num_frozen_list or None if we can't improve it
    num_frozen_list = []
    if cur_num_frozen_list == []:
    # First time around, so there is nothing to improve
    # Provide list that maximizes accuracy
        for app in apps:
            accs = app["accuracies"]
            max_acc = max(accs.values())
            best_num_frozen = \
                    max([k for k, v in accs.iteritems() if v == max_acc])
            num_frozen_list.append(best_num_frozen)
    else:
    # Find next frozen layer to get the lowest acc degradation
        min_accuracy_loss = float("inf")
        target_app_index = None
        target_num_frozen = None
        for index, app in enumerate(apps):
            cur_num_frozen = cur_num_frozen_list[index]

            rel_acc = get_relative_accuracy(app, cur_num_frozen)
            potential_num_frozen = get_next_frozen_layer(app, cur_num_frozen)
            potential_rel_acc = \
                    get_relative_accuracy(app, potential_num_frozen)
            potential_loss = potential_rel_acc - rel_acc
            print potential_loss
            if potential_loss < min_accuracy_loss:
                min_accuracy_loss = potential_loss
                target_app_index = index
                target_num_frozen = potential_num_frozen
        if min_accuracy_loss == 0:
        # There was no better schedule
            return None
        else:
        # Make improved num_frozen_list
            num_frozen_list = cur_num_frozen_list
            num_frozen_list[target_app_index] = target_num_frozen
    return num_frozen_list

