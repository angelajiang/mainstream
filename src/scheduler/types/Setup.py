import random 
import ConfigParser

class Setup:
  def __init__(self):
    self.apps = []
    self.video_desc  = {}
    self.id = random.choice(range(100))
    
  def __repr__(self):
    summary = "(id:{})".format(self.id)
    return summary

class SetupGenerator:

  def __init__(self, config_file):
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(config_file)

    self.budget_min = config_parser.get("config", "budget_min")
    self.budget_max = config_parser.get("config", "budget_max")
    self.budget_delta = config_parser.get("config", "budget_delta")
    self.correlation_min = config_parser.get("config", "correlation_min")
    self.correlation_max = config_parser.get("config", "correlation_max")
    self.correlation_delta = config_parser.get("config", "correlation_delta")
    self.event_frequency_min = config_parser.get("config", "event_frequency_min")
    self.event_frequency_max = config_parser.get("config", "event_frequency_max")
    self.event_frequency_delta = config_parser.get("config", "event_frequency_delta")
    self.event_length_ms_min = config_parser.get("config", "event_length_ms_min")
    self.event_length_ms_max = config_parser.get("config", "event_length_ms_max")
    self.event_length_ms_delta = config_parser.get("config", "event_length_ms_delta")

  def get_random_setup(self):

    return Setup()

  def get_setups(self, num_setups):

    setups = []

    for i in range(num_setups):
      setup = self.get_random_setup()
      while setup in setups:
        setup = self.get_random_setup()
      setups.append(setup)

    return setups

