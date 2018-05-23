#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <memory>
#include <limits>
#include <string>
#include <vector>
#include <unordered_map>
#include "types/schedule_unit.h"
#include "types/schedule.h"
#include "data.h"

std::unordered_map<std::string, int>  get_next_configuration(
  std::unordered_map<std::string, int> config,
  std::unordered_map<std::string, std::vector<ScheduleUnit>> possible_configs,
  std::vector<std::string> app_ids) {
  // Note: Vector of app_ids is used to maintain ordering
  // If we haven't returned config yet, the last index "overflowed"
  // and there are no more configurations.

  // Initialization case
  if (config.size() == 0){
    for (auto const & app_id : app_ids) {
      config.insert(make_pair(app_id, 0));
    }
    return config;
  }

  // "Increment" config
  for (auto const & app_id : app_ids) {
    int num_options = possible_configs[app_id].size();
    int next_index = config[app_id] + 1;
    if (next_index + 1  <= num_options) {
      config[app_id] = next_index;
      return config;
    }
    config[app_id] = 0;
  }

  return {};
}

// For a given schedule-configuration, get the optimal schedule
// TODO: Prune possible configurations
std::shared_ptr<Schedule> get_optimal_schedule(
  std::vector<std::string> app_ids,
  std::unordered_map<std::string, std::vector<ScheduleUnit>> possible_configurations,
  std::vector<double> layer_costs,
  int budget,
  int verbose)
{

  double min_metric = std::numeric_limits<double>::infinity();
  std::shared_ptr<Schedule> best_schedule = std::make_shared<Schedule>(layer_costs, budget);
  int config_count = 0;

  std::unordered_map<std::string, int> config = {};

  config = get_next_configuration(config, possible_configurations, app_ids);

  while (config.size() > 0) {
    std::shared_ptr<Schedule> schedule = std::make_shared<Schedule>(layer_costs, budget);

    // Since config is unordered, use app_ids for a consistent ordering
    for (auto const& app_id : app_ids) {
      int config_index = config[app_id];
      ScheduleUnit unit = possible_configurations[app_id][config_index];
      schedule->AddApp(unit);
    }

    double cost = schedule->GetCost();
    double average_metric = schedule->GetAverageMetric();
    if (average_metric < min_metric - EPSILON && cost < budget + EPSILON) {
      min_metric = average_metric;
      best_schedule = schedule;
      if (verbose > 0) {
        std::cout << "Metric: " << min_metric << "\n";
        std::cout << (*schedule) << ",";
        std::cout << schedule->GetCost() << "\n\n";
      }
    }

    config = get_next_configuration(config, possible_configurations, app_ids);

    if (config_count % 10000000 == 0) {
      std::cout << "Config count: " << config_count << "\n";
    }

    ++config_count;
  }

  return best_schedule;
}

int main(int argc, char *argv[]) {
  int i;
  double correlation_override = -1.0;

	  // parse command line
  i = 1;
  while((i < argc) && (*argv[i] == '-') && (*(argv[i]+1) == '-')) {
    if(string(argv[i]) == "--correlation_override") {
      correlation_override = strtod(argv[++i], NULL);
    } else {
      cout << "unknown command line option: " << argv[i] << std::endl;
      usage(argv[0]);
    }
    ++i;
  }
  if(argc != (i+3))
    usage(argv[0]); 

  std::string data_dir = argv[i];
  std::string setup_suffix = argv[++i];
  int budget = strtod(argv[++i], NULL);
  bool debug = false;
  std::cout << setup_suffix << ", " << data_dir << "\n";
  run("exhaustive.mainstream", data_dir, setup_suffix, get_optimal_schedule, budget, correlation_override, debug);
  return 0;
}
