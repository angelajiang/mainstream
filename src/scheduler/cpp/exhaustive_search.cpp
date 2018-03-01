#include <fstream>
#include <iostream>
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

/*
def get_cost_schedule(schedule, layer_latencies, num_layers):
    ### Cost of full schedule
    ### Measure based on sum of inference/sec of each layer
    # Schedule = [ScheduleUnit...]
    branch_points = list(set([unit.num_frozen for unit in schedule]))
    branch_points.append(num_layers)
    seg_start = 0
    cost = 0
    for seg_end in branch_points:
        seg_latency = sum([layer_latencies[i] for i in range(seg_start, seg_end)]) #doublecheck

        apps_branched, apps_not_branched = get_apps_branched(schedule, seg_end)
        seg_fps = 0
        branched_fpses = [unit.target_fps for unit in apps_branched]
        not_branched_fpses = [unit.target_fps for unit in apps_not_branched]
        if len(apps_branched) > 0: #double check
            task_fps = sum(branched_fpses)
            seg_fps += task_fps
        if len(apps_not_branched) > 0: #double check
            base_fps = max(not_branched_fpses)
            seg_fps += base_fps

        cost += seg_latency * seg_fps
        seg_start = seg_end

    return cost
 */

// Get cost of entire schedule
double get_schedule_cost(Schedule schedule,
                         vector<double> layer_costs,
                         int num_layers)
{

  return 0.0;
}

// For a given schedule-configuration, get the optimal schedule
Schedule get_optimal_schedule(string configurations_file,
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

  Schedule schedule = Schedule();

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
