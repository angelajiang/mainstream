import uuid
import numpy as np
import random
import sys
import App
import Architecture
import ConfigParser
import Video

sys.path.append('data')
import app_instance_data

# TODO: Integrate Model

class Setup:
  def __init__(self, apps, budget, video_desc):
    self.uuid = str(uuid.uuid4())[:8]
    self.apps = apps
    self.budget = budget
    self.video_desc  = video_desc

  def __repr__(self):
    summary = "{}:{}:{}".format(self.budget, self.video_desc, str(self.apps))
    return summary

class SetupGenerator:

  def __init__(self, config_file, random_state=1337):
    """Pass in random_state=None explicitly to have a non-fixed seed."""
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(config_file)
    self.rand = random.Random(random_state)

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


  def get_random_app(self):

    correlation = self.rand.choice(self.correlation_options)
    event_frequency = self.rand.choice(self.event_frequency_options)
    event_length_ms  = self.rand.choice(self.event_length_ms_options)
    app_uuid = str(uuid.UUID(int=self.rand.getrandbits(128)))[:8]

    app_index = self.rand.choice(range(len(App.AppInstance))) + 1
    app_type = App.AppInstance(app_index)

    app = app_instance_data.get_app_instance(app_type)

    app.event_length_ms = event_length_ms
    app.event_frequency = event_frequency
    app.correlation = correlation
    app.name = app.name + "-" + app_uuid

    return app


  def get_random_setup(self, num_apps, stream_fps):
    budget = self.rand.choice(self.budget_options)
    apps = []

    video = Video.Video(stream_fps)

    for i in range(num_apps):
      app = self.get_random_app()
      apps.append(app)

    return Setup(apps, budget, video)


  def get_setups(self, num_setups, num_apps, stream_fps):

    setups = []

    for i in range(num_setups):
      setup = self.get_random_setup(num_apps, stream_fps)
      setups.append(setup)

    return setups

