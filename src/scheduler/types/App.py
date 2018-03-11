from enum import Enum

class App:
  def __init__(self, name,
                     architecture,
                     accuracies,
                     prob_tnrs,
                     model_paths,
                     event_length_ms,
                     event_frequency,
                     correlation_coefficient):

    self.name = name
    self.architecture = architecture
    self.accuracies = accuracies
    self.prob_tnrs = prob_tnrs
    self.model_paths = model_paths
    self.event_length_ms = event_length_ms
    self.event_frequency = event_frequency
    self.correlation_coefficient = correlation_coefficient

  def __repr__(self):
    summary = "[{},{},{},{}]".format(self.name,
                                     self.event_length_ms,
                                     self.event_frequency,
                                     self.correlation_coefficient)
    return summary

  def __str__(self):
    summary = "[{},{},{},{}]".format(self.name,
                                     self.event_length_ms,
                                     self.event_frequency,
                                     self.correlation_coefficient)
    return summary

  def to_map(self):
    return {
            "app_id": self.name,
            "accuracies": self.accuracies,
            "prob_tnrs": self.prob_tnrs,
            "event_length_ms": self.event_length_ms,
            "event_frequency": self.event_frequency,
            "correlation_coefficient": self.correlation_coefficient,
            "model_path": self.model_paths
            }

class AppInstance(Enum):

  flowers_mobilenets224 = 1
  cars_mobilenets224 = 2
  cats_mobilenets224 = 3
  train_mobilenets224 = 4
  pedestrian_mobilenets224 = 5

