from enum import Enum
import hashlib
import uuid

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


  def get_id(self):
    ## WARNING: app_id depends on fields. App_id will change if field changes ##

    accuracies_str = ",".join([str(round(acc,4)) for acc in self.accuracies.values()])
    prob_tnrs_str = ",".join([str(round(prob_tnr,4)) for prob_tnr in self.prob_tnrs.values()])
    seed = str(self.architecture) + \
           accuracies_str + \
           prob_tnrs_str + \
           str(round(self.event_length_ms,4)) + \
           str(round(self.event_frequency,4)) + \
           str(round(self.correlation_coefficient,4))

    hash_obj = hashlib.sha1(seed)
    app_uuid = hash_obj.hexdigest()[:8]

    return self.name + ":" + app_uuid

  def to_map(self):
    return {
            "app_id": self.get_id(),
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
  bus_mobilenets224 = 6
  schoolbus_mobilenets224 = 7
  redcar_mobilenets224 = 8
  scramble_mobilenets224 = 9
