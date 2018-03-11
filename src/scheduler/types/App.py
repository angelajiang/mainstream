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
    summary = "(App {}, {})".format(self.name, self.architecture.name)
    return summary

  def to_map(self):
    return {
            "name": self.name,
            "accuracies": self.accuracies,
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

  #flowers_inceptionv3 = 2
  #flowers_resnet50 = 3
  #cars_inceptionv3 = 5
  #cars_resnet50 = 6
  #cats_inceptionv3 = 8
  #cats_resnet50 = 9


    
