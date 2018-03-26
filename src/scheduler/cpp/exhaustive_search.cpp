#include <chrono>
#include <fstream>
#include <iostream>
#include <memory>
#include <limits>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"
#include "schedule.h"

using namespace std;

// TODO: add more comments

typedef unsigned int app_num_t; // each app will have a unique id
typedef unordered_map<string, app_num_t> app_map_t; // associate app names with ids

// set of possible (sharing, framerate, cost, metric) settings for an app
typedef vector<ScheduleUnit> app_settings_vec_t; 
// Data structure, indexed by app_num, where each element is an app_settings_vec_t; 
typedef vector< app_settings_vec_t > appset_config_vov_t; // vector of vectors

// Parse input files
void parse_configurations_file(const string configurations_file,
			       app_map_t &app_map, appset_config_vov_t &appset_settings)
{
  std::ifstream infile(configurations_file);
  string app_name;
  int num_frozen, fps;
  double cost, metric;

  // the data structures are assumed to be empty, initially
  if((app_map.size()!=0) || (appset_settings.size()!=0))
    throw(logic_error("nonempty data structure when parsing configurations file."));

  // read the file
  while (infile >> app_name >> num_frozen >> fps >> cost >> metric)
  {
    // form the app setting
    ScheduleUnit unit = ScheduleUnit(app_name, num_frozen, fps, cost, metric);

    app_num_t app_id;

    // find the app_id for this setting
    if (app_map.find(app_name) == app_map.end()) {
      // "allocate" new app id for this name
      app_id = appset_settings.size();
      app_map[app_name] = app_id;
      app_settings_vec_t tmp={};
      appset_settings.push_back(tmp);
    } else {
      app_id = app_map[app_name];
    }

    // add the setting to the app
    vector<ScheduleUnit> &units = appset_settings[app_id];
    units.push_back(unit);
  }
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

void get_next_configuration(unordered_map<string, int> & config,
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
    return;
  }

  // "Increment" config
  for (auto const & app_id : app_ids) {
    int num_options = possible_configs[app_id].size();
    int next_index = config[app_id] + 1;
    if (next_index + 1  <= num_options) {
      config[app_id] = next_index;
      return;
    }
    config[app_id] = 0;
  }

  config = {};

  return;
}

// For a given schedule-configuration, get the optimal schedule
// TODO: Prune possible configurations
shared_ptr<Schedule> get_optimal_schedule(const appset_config_vov_t appset_settings,
					  // unordered_map<string, vector<ScheduleUnit>> possible_configurations,
                                          const vector<double> layer_costs,
                                          double budget,
                                          bool debug)
{
  app_num_t n;
  
  app_num_t num_apps = appset_settings.size();
    
  // schedule currently under consideration -- we assume an index for each of the possible settings
  //   for each of the app_ids
  vector<unsigned> config(num_apps, 0);
  // for(n=0; n<num_apps; n++)  config.push_back(0);   // intialize config
  
  double min_metric = numeric_limits<double>::infinity();
  shared_ptr<Schedule> best_schedule = make_shared<Schedule>(layer_costs, budget);
  int config_count = 0;

  bool done = false;
  while (!done) {
    shared_ptr<Schedule> schedule = make_shared<Schedule>(layer_costs, budget);

    for (n=0; n<num_apps; n++) {
      int app_setting_index = config[n];
      ScheduleUnit unit = appset_settings[n][app_setting_index];
      schedule->AddApp(unit);
    }

    double cost = schedule->GetCost();
    double average_metric = schedule->GetAverageMetric();

    if (average_metric < min_metric && cost < budget){
      min_metric = average_metric;
      best_schedule = schedule;
      if (debug) {
        cout << "Metric: " << min_metric << "\n";
        cout << (*schedule) << ",";
        cout << schedule->GetCost() << "\n\n";
      }
    }

    // "Increment" config
    done = true; // assume for now
    for (n=0; n<num_apps; n++) {
      int num_options = appset_settings[n].size();
      int next_option_index = config[n] + 1;
      if (next_option_index + 1  <= num_options) {
	config[n] = next_option_index;
	done = false; // found untried config
	break;
      }	
      config[n] = 0;
    }

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

    cout << "Getting optimal schedule for config " << id << "\n" << flush;

    app_map_t app_map;
    appset_config_vov_t app_settings;
    parse_configurations_file(configurations_file, app_map, app_settings);

    vector<double> layer_costs = parse_model_file(model_file);
    double budget = parse_environment_file(environment_file);

    auto start = chrono::high_resolution_clock::now();

    shared_ptr<Schedule> sched = get_optimal_schedule(app_settings,
                                                      layer_costs,
                                                      budget,
                                                      debug);

    auto elapsed = chrono::high_resolution_clock::now() - start;
    long microseconds = chrono::duration_cast<std::chrono::microseconds>(elapsed).count();

    cout << (*sched) << "\n";

    outfile << sched->GetOutputLine() << "," << microseconds << "\n";

    outfile.flush();
  }

  outfile.close();
}

int main(int argc, char *argv[])
{
  string data_dir = argv[1];
  string setup_suffix = argv[2];
  bool debug = true;
  cout << setup_suffix << ", " << data_dir << "\n";
  run(data_dir, setup_suffix, debug);
}
