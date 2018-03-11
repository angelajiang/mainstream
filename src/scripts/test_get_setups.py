import pprint as pp
import sys
sys.path.append('src/scheduler/types')

import Setup

def main():

  config_file = "config/scheduler/setup.v0"
  num_setups = 10
  num_apps = 5
  architecture = 1

  setup_generator = Setup.SetupGenerator(config_file)
  setups = setup_generator.get_setups(num_setups, num_apps, architecture)
  assert len(setups) == num_setups
  pp.pprint(setups)

if __name__ == "__main__":
  main()

