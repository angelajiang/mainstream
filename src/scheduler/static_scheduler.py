import sys
sys.path.append('src/scheduler')
import scheduler


def get_num_frozen(accs, threshold):
    max_acc = max(accs.values())
    acc_threshold = max_acc - (threshold * max_acc)
    max_layers_frozen = \
        max([layers_frozen \
            for layers_frozen, accuracy in accs.iteritems()  \
            if accuracy >= acc_threshold])
    return max_layers_frozen

def schedule(apps, threshold, model_desc):

    if threshold == 0:
        return scheduler.schedule_no_sharing(apps, model_desc)

    num_frozen_list = []
    for app in apps:
        accs = app["accuracies"]
        num_frozen = get_num_frozen(accs, threshold)
        num_frozen_list.append(num_frozen)

    return scheduler.schedule(apps, num_frozen_list, model_desc)

