from enum import Enum
import uuid

class App:
  def __init__(self, class_name,
                     architecture,
                     accuracies,
                     prob_tnrs,
                     model_paths,
                     event_length_ms,
                     event_frequency,
                     correlation_coefficient):

    self.class_name = class_name
    self.app_id = class_name + "-" + str(uuid.uuid4())[:8]
    self.architecture = architecture
    self.accuracies = accuracies
    self.prob_tnrs = prob_tnrs
    self.model_paths = model_paths
    self.event_length_ms = event_length_ms
    self.event_frequency = event_frequency
    self.correlation_coefficient = correlation_coefficient

  def __repr__(self):
    summary = "[{},{},{},{}]".format(self.class_name,
                                     self.event_length_ms,
                                     self.event_frequency,
                                     self.correlation_coefficient)
    return summary

  def __str__(self):
    summary = "[{},{},{},{}]".format(self.class_name,
                                     self.event_length_ms,
                                     self.event_frequency,
                                     self.correlation_coefficient)
    return summary

  def to_map(self):
    return {
            "app_id": self.app_id,
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

