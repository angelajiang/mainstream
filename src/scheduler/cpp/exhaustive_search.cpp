#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <memory>
#include <limits>
#include <vector>
#include <unordered_map>
#include "types/schedule_unit.h"
#include "types/schedule.h"
#include "data.h"

using namespace std;

unordered_map<string, int> get_next_configuration(unordered_map<string, int> config,
                                                  unordered_map<string, vector<ScheduleUnit>> possible_configs,
                                                  vector<string> app_ids)
{
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
shared_ptr<Schedule> get_optimal_schedule(
  std::vector<string> app_ids,
  unordered_map<string, vector<ScheduleUnit>> possible_configurations,
  vector<double> layer_costs,
  double budget,
  int verbose)
{

  vector<string> keys;
  keys.reserve(possible_configurations.size());
  for (auto kv: possible_configurations) {
    keys.push_back(kv.first);
  }
  std::sort(keys.begin(), keys.end());

  double min_metric = numeric_limits<double>::infinity();
  shared_ptr<Schedule> best_schedule = make_shared<Schedule>(layer_costs, budget);
  int config_count = 0;

  unordered_map<string, int> config = {};

  config = get_next_configuration(config, possible_configurations, keys);

  while (config.size() > 0) {

    shared_ptr<Schedule> schedule = make_shared<Schedule>(layer_costs, budget);

    // Since config is unordered, use app_ids for a consistent ordering
    for (auto const& app_id : keys) {
      int config_index = config[app_id];
      ScheduleUnit unit = possible_configurations[app_id][config_index];
      schedule->AddApp(unit);
    }

    double cost = schedule->GetCost();
    double average_metric = schedule->GetAverageMetric();
    if (average_metric < min_metric - EPSILON && cost < budget + EPSILON){
      min_metric = average_metric;
      best_schedule = schedule;
      if (verbose > 0) {
        cout << "Metric: " << min_metric << "\n";
        cout << (*schedule) << ",";
        cout << schedule->GetCost() << "\n\n";
      }
    }

    config = get_next_configuration(config, possible_configurations, keys);

    if (config_count % 10000000 == 0) {
      cout << "Config count: " << config_count << "\n";
    }

    ++config_count;
  }

  return best_schedule;
}

int main(int argc, char *argv[]) {
  std::string data_dir = argv[1];
  std::string setup_suffix = argv[2];
  bool debug = false;
  std::cout << setup_suffix << ", " << data_dir << "\n";
  run("exhaustive", data_dir, setup_suffix, get_optimal_schedule, debug);
  return 0;
}