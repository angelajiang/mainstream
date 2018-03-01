#include <fstream>
#include <iostream>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"

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
    cout << app_id << ",";
    cout << num_frozen << ",";
    cout << fps << ",";
    cout << cost << ",";
    cout << metric << "\n";

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
  return layer_costs;
}

// Get cost of entire schedule
double get_schedule_cost(vector<ScheduleUnit> schedule,
                         vector<double> layer_costs,
                         int num_layers)
{
  return 0.0;
}

// For a given schedule-configuration, get the optimal schedule
vector<ScheduleUnit> get_optimal_schedule(string configurations_file,
                                          string model_file)
{
  unordered_map<int, vector<ScheduleUnit>> possible_configurations = 
    parse_configurations_file(configurations_file);
  vector<double> layer_costs = parse_model_file(model_file);
  int num_layers = layer_costs.size();

  // TODO: Prune possible configurations

  // Exhaustively search possible schedules
  for (auto const& app : possible_configurations) {
    int app_id = app.first;
    vector<ScheduleUnit> app_options = app.second;
    cout << app_id << ": ";
    cout << app_options.size() << "\n";

  }


  vector<ScheduleUnit> schedule = {};

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
