
class Model:
    def __init__(self, model_desc):
        self.channels = model_desc["channels"]
        self.height = model_desc["height"]
        self.width = model_desc["width"]
        self.final_layer = model_desc["total_layers"]
        self.layer_latencies = model_desc["layer_latencies"]
        self.frozen_layer_names = model_desc["frozen_layer_names"]

class NeuralNet:
    # Represents a Streamer unit -- a NeuralNetEvaluator
    def __init__(self, net_id, app_id, model_obj, parent_id=None, start=None,
                       end=None, shared=None, target_fps=None, model_path=None):
        self.net_id = net_id

        self.data = {"net_id": self.net_id,
                     "app_id": app_id,
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
        if target_fps != None:
            self.data["target_fps"] = target_fps
        if shared != None:
            self.shared = shared
            self.data["shared"] = shared
        if model_path != None:
            self.model_path = model_path
            self.data["model_path"] = model_path

    def __str__(self):
        return self.data

class StreamerSchedule:
    # Represents a Streamer schedule
    def __init__(self):
        self.next_id = 0
        self.schedule = []

    def add_neural_net(self, net):
        self.schedule.append(net.data)

    def get_id(self):
        next_id = self.next_id
        self.next_id += 1
        return next_id

class ScheduleUnit:
    # Represents a Mainstream schedule unit
    def __init__(self, app, target_fps, num_frozen):
        self.app = app
        self.app_id = app["app_id"]
        self.target_fps = target_fps
        self.num_frozen = num_frozen

    def __str__(self):
        return 'App(id={},fps={},nf={})'.format(self.app_id, self.target_fps, self.num_frozen)



