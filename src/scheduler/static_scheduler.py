
class NeuralNet:
    def __init__(self, net_id, model_obj, parent_id=None, start=None,
                       end=None, shared=None, model_path=None):
        self.net_id = net_id

        self.data = {"net_id": self.net_id,
                     "channels": model_obj.channels,
                     "width": model_obj.width,
                     "height": model_obj.height}

        if parent_id != None:
            self.parent_id = parent_id
            self.data["parent_id"] = parent_id
        if start != None:
            self.start = start
            self.data["input_layer"] = model_obj.frozen_layer_names[start]
        if end != None:
            self.end = end
            if end != 0:            # Starting condition
                self.data["output_layer"] = model_obj.frozen_layer_names[end]
        if shared != None:
            self.shared = shared
            self.data["shared"] = shared
        if model_path != None:
            self.model_path = model_path
            self.data["model_path"] = model_path

    def __str__(self):
        return self.data

class Model:
    def __init__(self, model_desc):
        self.channels = model_desc["channels"]
        self.height = model_desc["height"]
        self.width = model_desc["width"]
        self.final_layer = model_desc["total_layers"]
        self.frozen_layer_names = model_desc["frozen_layer_names"]

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

def schedule_no_sharing(apps, model_desc):

    model = Model(model_desc)
    s = Schedule()

    for app in apps:
        net = NeuralNet(s.get_id(),
                        model,
                        -1,
                        1,
                        model.final_layer,
                        False,
                        app["model_path"])
        s.add_neural_net(net)
    return s.schedule


def schedule(apps, threshold, model_desc):

    for app in apps:
        accs = app["accuracies"]
        num_frozen = get_num_frozen(accs, threshold)
        app["num_frozen"] = num_frozen

    model = Model(model_desc)
    s = Schedule()

    num_apps_done = 0
    last_shared_layer = 1

    parent_net = NeuralNet(-1, model, end=1)

    while (num_apps_done < len(apps)):
        min_frozen = min([app["num_frozen"] \
            for app in apps if app["num_frozen"] > last_shared_layer])
        min_apps = [app for app in apps if app["num_frozen"] == min_frozen]
        future_apps = [app for app in apps if app["num_frozen"] > min_frozen]

        # Check if we need to share part of the NN, and make a base NN
        # If so, we make it and set it as the parent
        if len(future_apps) > 0 or len(min_apps) == len(apps):
            net = NeuralNet(s.get_id(),
                            model,
                            parent_net.net_id,
                            last_shared_layer,
                            min_frozen,
                            True,
                            min_apps[0]["model_path"])
            s.add_neural_net(net)
            parent_net = net

        # Make app-specific NN that is branched off the parent - (either nothing
        # or the last shared branch)
        for app in min_apps:
            net = NeuralNet(s.get_id(),
                            model,
                            parent_net.net_id,
                            parent_net.end,
                            model.final_layer,
                            False,
                            app["model_path"])
            s.add_neural_net(net)
            num_apps_done += 1

        last_shared_layer = parent_net.end

    return s.schedule

