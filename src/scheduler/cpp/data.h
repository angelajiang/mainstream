#ifndef DATA_H
#define DATA_H

#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include "schedule_unit.h"

unordered_map<std::string, std::vector<ScheduleUnit>> parse_configurations_file(
    std::string configurations_file) {
  std::ifstream infile(configurations_file);
  std::string app_id;
  int num_frozen, fps;
  double cost, metric;
  std::unordered_map<std::string, std::vector<ScheduleUnit>>
      possible_configurations = {};
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
  double budget;

  std::ifstream infile(environment_file);
  if (infile.good()) {
    infile >> budget;
  }

  return budget;
}

#endif  // DATA_H
