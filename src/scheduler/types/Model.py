
class Model():

  def __init__(self, name,
                     architecture,
                     total_layers,
                     channels,
                     height,
                     width,
                     layer_costs,
                     chokepoint_names):
    self.name = name
    self.architecture = architecture
    self.total_layers = total_layers
    self.channels = channels
    self.height = height
    self.width = width
    self.layer_costs = layer_costs
    self.chokepoint_names = chokepoint_names

  def to_map(self):
    return {
            "name": self.name,
            "total_layer": self.total_layer,
            "channels": self.channels,
            "height": self.height,
            "width": self.width,
            "layer_latencies": self.layer_costs,
            "frozen_layer_names": self.chokepoint_names,
            }

