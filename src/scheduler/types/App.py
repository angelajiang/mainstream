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
    self.event_length_ms = event_length_ms
    self.event_frequency = event_frequency
    self.correlation_coefficient = correlation_coefficient
    self.model_paths = model_paths

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

    
