#include <fstream>
#include <iostream>
#include <memory>
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
  std::string delimiter = ",";
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
  }
  return layer_costs;
}

// For a given schedule-configuration, get the optimal schedule
unique_ptr<Schedule> get_optimal_schedule(string configurations_file,
                                          string model_file)
{
  unordered_map<int, vector<ScheduleUnit>> possible_configurations = 
    parse_configurations_file(configurations_file);
  vector<double> layer_costs = parse_model_file(model_file);
  int num_layers = layer_costs.size();

  // TODO: Prune possible configurations

  // Exhaustively search possible schedules
  unique_ptr<Schedule> schedule = make_unique<Schedule>(layer_costs);
  for (auto const& app : possible_configurations) {
    int app_id = app.first;
    vector<ScheduleUnit> app_options = app.second;
    schedule->AddApp(app_options.at(0));
  }

  schedule->GetCost();

  return schedule;
}

int main()
{
  string configurations_file = "data/cpp/configurations/test.v0";
  string model_file = "data/cpp/models/test.v0";
  get_optimal_schedule(configurations_file,
                       model_file);

  cout << "Hello world!\n";
}
