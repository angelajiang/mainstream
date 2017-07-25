
class NeuralNet:
    def __init__(self, net_id, parent_id=None, start=None,
                       end=None, model_path=None):
        self.net_id = net_id
        if parent_id != None:
            self.parent_id = parent_id
        if start != None:
            self.start = start
        if end != None:
            self.end = end
        if model_path != None:
            self.model_path = model_path

        self.data = {"net_id": net_id,
                     "parent_id": parent_id,
                     "start": start,
                     "end": end,
                     "model_path": model_path}
    def __str__(self):
        return self.data

class Schedule:
    def __init__(self):
        self.next_id = 0
        self.schedule = []

    def add_neural_net(self, net):
        self.schedule.append(net.data)

    def get_id(self):
        next_id = self.next_id
        self.next_id += 1
        return next_id


def get_num_frozen(accs, threshold):
    max_acc = max(accs.values())
    acc_threshold = max_acc - (threshold * max_acc)
    max_layers_frozen = \
        max([layers_frozen \
            for layers_frozen, accuracy in accs.iteritems()  \
            if accuracy >= acc_threshold])
    return max_layers_frozen

def schedule(apps, threshold, final_layer):
    for app in apps:
        accs = app["accuracies"]
        num_frozen = get_num_frozen(accs, threshold)
        app["num_frozen"] = num_frozen

    s = Schedule()

    num_apps_done = 0
    last_shared_layer = 0

    parent_net = NeuralNet(-1, end=0)

    while (num_apps_done < len(apps)):
        min_frozen = min([app["num_frozen"] \
            for app in apps if app["num_frozen"] > last_shared_layer])
        min_apps = [app for app in apps if app["num_frozen"] == min_frozen]
        future_apps = [app for app in apps if app["num_frozen"] > min_frozen]
        if (len(future_apps) > 0):
            # We need to split the NN
            net = NeuralNet(s.get_id(),
                           parent_net.net_id,
                           last_shared_layer + 1,
                           min_frozen,
                           min_apps[0]["model_path"])
            s.add_neural_net(net)
            parent_net = net
        # Make app specific NN
        for app in min_apps:
            net = NeuralNet(s.get_id(),
                            parent_net.net_id,
                            parent_net.end + 1,
                            final_layer,
                            app["model_path"])
            s.add_neural_net(net)
            num_apps_done += 1

        last_shared_layer = parent_net.end

    return s.schedule

