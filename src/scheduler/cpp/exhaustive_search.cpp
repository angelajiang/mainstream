#include <fstream>
#include <iostream>
#include <memory>
#include <limits>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"
#include "schedule.h"

using namespace std;


// Parse input files
unordered_map<int, vector<ScheduleUnit>>
  parse_configurations_file(string configurations_file)
{
  std::ifstream infile(configurations_file);
  int app_id, num_frozen, fps;
  double cost, metric;
  unordered_map<int, vector<ScheduleUnit>> possible_configurations = {};
  while (infile >> app_id >> num_frozen >> fps >> cost >> metric)
  {
    vector<ScheduleUnit> units; 
    ScheduleUnit unit = ScheduleUnit(app_id, num_frozen, fps, cost, metric);

    if (possible_configurations.find(app_id) == possible_configurations.end()) {
      units = {};
    } else {
      units = possible_configurations[app_id];
    }
    units.push_back(unit);
    possible_configurations.insert(make_pair(app_id, units));
    possible_configurations[app_id] = units;

  }
  return possible_configurations;
}

vector<double> parse_model_file(string model_file)
{
  vector<double> layer_costs = {};

  std::ifstream infile(model_file);
  std::string delimiter = " ";
  if (infile.good())
  {
    string line;
    getline(infile, line);

    size_t pos = 0;
    double token;
    std::string token_str;
    std::string::size_type sz;

    while ((pos = line.find(delimiter)) != std::string::npos) {
          token_str = line.substr(0, pos);
          token = stod(token_str, &sz);
          layer_costs.push_back(token);
          line.erase(0, pos + delimiter.length());
    }

    token_str = line.substr(0, pos);
    token = stod(token_str, &sz);
    layer_costs.push_back(token);
    line.erase(0, pos + delimiter.length());
  }
  return layer_costs;
}

double parse_environment_file(string environment_file)
{
  double budget;

  std::ifstream infile(environment_file);
  if (infile.good()) {
    infile >> budget;
  }

  return budget;
}

unordered_map<int, int> get_next_configuration(unordered_map<int, int> config,
                                               unordered_map<int, vector<ScheduleUnit>> possible_configs,
                                               vector<int> app_ids){
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
shared_ptr<Schedule> get_optimal_schedule(unordered_map<int, vector<ScheduleUnit>> possible_configurations,
                                          vector<double> layer_costs,
                                          double budget,
                                          bool debug) {

  vector<int> keys;
  keys.reserve(possible_configurations.size());
  for (auto kv: possible_configurations) {
    keys.push_back(kv.first);
  }

  double min_metric = numeric_limits<double>::infinity();
  shared_ptr<Schedule> best_schedule = make_shared<Schedule>(layer_costs, budget);
  int config_count = 0;

  unordered_map<int, int> config = {};
  config = get_next_configuration(config, possible_configurations, keys);

  while (config.size() > 0) {

    shared_ptr<Schedule> schedule = make_shared<Schedule>(layer_costs, budget);

    for (auto const& c : config) {
      int app_id = c.first;
      int config_index = c.second;
      ScheduleUnit unit = possible_configurations[app_id][config_index];
      schedule->AddApp(unit);
    }

    double cost = schedule->GetCost();
    double average_metric = schedule->GetAverageMetric();

    if (average_metric < min_metric && cost < budget){
      min_metric = average_metric;
      best_schedule = schedule;
      if (debug) {
        cout << "Metric: " << metric << "\n";
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

void run(string data_dir, string pointer_suffix, bool debug)
{
  string pointers_file = data_dir + "/pointers." + pointer_suffix;
  ifstream infile(pointers_file);

  string results_file = data_dir + "/schedules/exhaustive." + pointer_suffix;
  ofstream outfile(results_file);

  string id;

  while (infile >> id)
  {
    string configurations_file = data_dir + "/setup/configuration." + id;
    string model_file = data_dir + "/setup/model." + id ;
    string environment_file = data_dir + "/setup/environment." + id;

    cout << "Getting optimal schedule for config " << id << "\n" << flush;;

    unordered_map<int, vector<ScheduleUnit>> possible_configurations = 
      parse_configurations_file(configurations_file);
    vector<double> layer_costs = parse_model_file(model_file);
    double budget = parse_environment_file(environment_file);

    shared_ptr<Schedule> sched = get_optimal_schedule(possible_configurations,
                                                      layer_costs,
                                                      budget,
                                                      debug);

    cout << (*sched) << "\n";

    outfile << sched->GetOutputLine() << "\n";
    outfile.flush();
  }

  outfile.close();
}

int main()
{
  string data_dir = "data/cpp";
  string pointer_suffix = "test.v0";
  bool debug = false;
  run(data_dir, pointer_suffix, debug);
}
