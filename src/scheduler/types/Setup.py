import uuid
import numpy as np
import random 
import App
import Architecture
import ConfigParser

class Setup:
  def __init__(self, apps, budget, video_desc):
    self.apps = apps
    self.budget = budget
    self.video_desc  = {}
    
  def __repr__(self):
    summary = "(Apps: {} Budget:{})".format(str(self.apps), self.budget)
    return summary

class SetupGenerator:

  def __init__(self, config_file):
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(config_file)

    budget_min = int(config_parser.get("config", "budget_min"))
    budget_max = int(config_parser.get("config", "budget_max"))
    budget_delta = int(config_parser.get("config", "budget_delta"))
    correlation_min = float(config_parser.get("config", "correlation_min"))
    correlation_max = float(config_parser.get("config", "correlation_max"))
    correlation_delta = float(config_parser.get("config", "correlation_delta"))
    event_frequency_min = float(config_parser.get("config", "event_frequency_min"))
    event_frequency_max = float(config_parser.get("config", "event_frequency_max"))
    event_frequency_delta = float(config_parser.get("config", "event_frequency_delta"))
    event_length_ms_min = int(config_parser.get("config", "event_length_ms_min"))
    event_length_ms_max = int(config_parser.get("config", "event_length_ms_max"))
    event_length_ms_delta = int(config_parser.get("config", "event_length_ms_delta"))

    self.budget_options = np.arange(budget_min,
                                    budget_max,
                                    budget_delta)
    self.correlation_options = np.arange(correlation_min,
                                         correlation_max,
                                         correlation_delta)
    self.event_frequency_options = np.arange(event_frequency_min,
                                             event_frequency_max,
                                             event_frequency_delta)
    self.event_length_ms_options = np.arange(event_length_ms_min,
                                             event_length_ms_max,
                                             event_length_ms_delta)

  def get_random_app(self, architecture):

    correlation = random.choice(self.correlation_options)
    event_frequency = random.choice(self.event_frequency_options)
    event_length_ms  = random.choice(self.event_length_ms_options)
    app_uuid = str(uuid.uuid4())[:8]
    accuracies = {}
    prob_tnrs = {}
    model_paths = {}

    arch = Architecture.Architecture(architecture)

    app =  App.App(app_uuid,
                   arch,
                   accuracies,
                   prob_tnrs,
                   model_paths,
                   event_length_ms,
                   event_frequency,
                   correlation)

    return app


  def get_random_setup(self, num_apps, architecture):
    budget = random.choice(self.budget_options)
    apps = []

    for i in range(num_apps):
      app = self.get_random_app(architecture)
      apps.append(app)

    return Setup(apps, budget, {})

  def get_setups(self, num_setups, num_apps, architecture):

    setups = []

    for i in range(num_setups):
      setup = self.get_random_setup(num_apps, architecture)
      setups.append(setup)

    return setups

