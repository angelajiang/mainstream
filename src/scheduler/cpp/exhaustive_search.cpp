#include <iostream>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"

using namespace std;



// Parse input files
unordered_map<int, vector<ScheduleUnit>>
  parse_configurations_file(string configurations_file)
{
  unordered_map<int, vector<ScheduleUnit>> possible_configurations = {};
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
    cout << app_id << "\n";
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
