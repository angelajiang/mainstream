import hashlib
import numpy as np
import random 
import os
import pickle
import sys
import uuid
import App
import Architecture
import ConfigParser
import Video

sys.path.append('data')
import app_instance_data

# TODO: Integrate Model

VERSION_SUFFIX = ".v0"

random.seed(1337)

class Setup:
  def __init__(self, apps, budget, video_desc):
    self.apps = apps
    self.budget = budget
    self.video_desc  = video_desc
    app_ids_str = ",".join([app.get_id() for app in self.apps])
    seed = app_ids_str + str(self.budget) + str(self.video_desc)
    hash_obj = hashlib.sha1(seed)
    self.uuid = hash_obj.hexdigest()[:8] + VERSION_SUFFIX
    print self.uuid

  def __repr__(self):
    summary = "{}:{}:{}".format(self.budget, self.video_desc, str(self.apps))
    return summary


class SetupGenerator:

  def parse_config(self, config_file):

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
    epsilon_min = float(config_parser.get("config", "epsilon_min"))
    epsilon_max = float(config_parser.get("config", "epsilon_max"))
    epsilon_delta = float(config_parser.get("config", "epsilon_delta"))
    yint_min = float(config_parser.get("config", "yint_min"))
    yint_max = float(config_parser.get("config", "yint_max"))
    yint_delta = float(config_parser.get("config", "yint_delta"))
    exponent_min = int(config_parser.get("config", "exponent_min"))
    exponent_max = int(config_parser.get("config", "exponent_max"))
    exponent_delta = int(config_parser.get("config", "exponent_delta"))

    self.budget_options = np.arange(budget_min,
                                    budget_max + budget_delta,
                                    budget_delta)
    self.correlation_options = np.arange(correlation_min,
                                         correlation_max + correlation_delta,
                                         correlation_delta)
    self.event_frequency_options = np.arange(event_frequency_min,
                                             event_frequency_max + event_frequency_delta,
                                             event_frequency_delta)
    self.event_length_ms_options = np.arange(event_length_ms_min,
                                             event_length_ms_max + event_length_ms_delta,
                                             event_length_ms_delta)

    self.num_param_setups = len(self.budget_options) * \
                            len(self.correlation_options) * \
                            len(self.event_frequency_options) * \
                            len(self.event_length_ms_options)


  def get_random_app(self, synthetic_curve=0):

    correlation = random.choice(self.correlation_options)
    event_frequency = random.choice(self.event_frequency_options)
    event_length_ms  = random.choice(self.event_length_ms_options)

    if synthetic_curve:
        app_index = 0
    else:
        app_index = random.choice(range(len(App.AppInstance) - 1)) + 1

    app_type = App.AppInstance(app_index)
    app = app_instance_data.get_app_instance(app_type)

    app.event_length_ms = event_length_ms
    app.event_frequency = event_frequency
    app.correlation = correlation

    if synthetic_curve:
        yint = random.choice(self.yint_options)
        epsilon = random.choice(self.episilon_options)
        exponent = random.choice(self.exponent_options)
        chokepoints = app.model_paths.keys()
        app.accuracies = app.generate_accuracies(yint, epsilon, exponent, chokepoints)
        app.prob_tnrs = app.generate_prob_tnrs(yint, epsilon, exponent, chokepoints)

    return app


  def get_random_setup(self, num_apps, stream_fps):

    budget = random.choice(self.budget_options)
    apps = []

    video = Video.Video(stream_fps)

    for i in range(num_apps):
      app = self.get_random_app()
      apps.append(app)

    return Setup(apps, budget, video)


  def generate_setups(self, num_setups, num_apps, stream_fps):

    setups = []

    for i in range(num_setups):
      setup = self.get_random_setup(num_apps, stream_fps)
      setups.append(setup)

    return setups


  def serialize_setups(self, setups, setups_file):

    with open(setups_file, "a+") as f:
        for setup in setups:
            setup_uuid = setup.uuid
            line = "{},{}\n".format(setup_uuid, setup)
            f.write(line)
            f.flush()

    setups_pickle_file = setups_file + ".pickle"
    with open(setups_pickle_file, "wb") as f:
        pickle.dump(setups, f)

  def deserialize_setups(self, setups_pickle_file):
    with open(setups_pickle_file, "rb") as f:
        return pickle.load(f)


