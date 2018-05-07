#include <algorithm>
#include <chrono>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include "data.h"

app_configs_t parse_configurations_file(
    std::string configurations_file) {
  std::ifstream infile(configurations_file);
  std::string app_id;
  int num_frozen, fps;
  double cost, metric;
  app_configs_t possible_configurations = {};
  while (infile >> app_id >> num_frozen >> fps >> cost >> metric) {
    std::vector<ScheduleUnit> units;
    ScheduleUnit unit = ScheduleUnit(app_id, num_frozen, fps, cost, metric);

    if (possible_configurations.find(app_id) == possible_configurations.end()) {
      units = {};
    } else {
      units = possible_configurations[app_id];
    }
    units.push_back(unit);
    possible_configurations[app_id] = units;
  }
  return possible_configurations;
}

std::vector<double> parse_model_file(std::string model_file) {
  std::vector<double> layer_costs = {};

  std::ifstream infile(model_file);
  std::string delimiter = " ";
  if (infile.good()) {
    std::string line;
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

double parse_environment_file(std::string environment_file) {
  int budget;

  std::ifstream infile(environment_file);
  if (infile.good()) {
    infile >> budget;
  }

  return budget;
}

void run(const std::string& scheduler_type,
         const std::string& data_dir,
         const std::string& pointer_suffix,
         scheduler_fn_ptr scheduler_fn,
         int budget,
         bool debug) {
  std::string pointers_file = data_dir + "/pointers." + pointer_suffix;
  std::ifstream infile(pointers_file);

  std::string results_file =
      data_dir + "/schedules/" + scheduler_type + ".sim." + std::to_string(budget) + "." + pointer_suffix;
  std::ofstream outfile(results_file);

  std::string id;

  while (infile >> id) {
    std::string configurations_file = data_dir + "/setup/configuration." + id;
    std::string model_file = data_dir + "/setup/model." + id;
    std::string environment_file = data_dir + "/setup/environment." + id;

    std::cout << "Getting optimal schedule for config " << id << "\n"
              << std::flush;

    app_configs_t possible_configurations =
      parse_configurations_file(configurations_file);

    layer_costs_t layer_costs = parse_model_file(model_file);

    auto start = std::chrono::high_resolution_clock::now();

    int num_apps;
    infile >> num_apps;
    std::vector<std::string> app_ids;
    for (int i = 0; i < num_apps; i++) {
      std::string app_id;
      infile >> app_id;
      app_ids.push_back(app_id);
    }

    std::shared_ptr<Schedule> sched = scheduler_fn(
      app_ids,
      possible_configurations,
      layer_costs,
      budget,
      debug);

    auto elapsed = std::chrono::high_resolution_clock::now() - start;
    auto microseconds =
        std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count();

    std::cout << (*sched) << "\n";

    outfile << id << "," <<  sched->GetOutputLine() << "," << microseconds << "\n";

    std::cout << "--------------------\n";

    outfile.flush();
  }

  outfile.close();
}
