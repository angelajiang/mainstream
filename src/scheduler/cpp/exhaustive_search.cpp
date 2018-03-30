#include <chrono>
#include <fstream>
#include <iostream>
#include <memory>
#include <limits>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include "schedule_unit.h"
#include "schedule.h"

using namespace std;

// Globals
bool debug = false;
double budget_override = 0.0;

// Helper data struct: simple vector of possible (sharing, framerate, cost, metric) settings for an app
typedef vector<ScheduleUnit> AppSettingsVec; 

// Helper comparator function
//   Return true if app configuration 'i' will have a larger impact on the *cost* of a mainstream
//     schedule than app configuration 'j'.  That will be true if i and j represent the same sharing
//     level but i's framerate is greater, or if i and j represent the same framerate, but i has
//     FEWER frozen layers.  Or both.  We return 'false' if both framerate and sharing are equal.
//   Also, note that not all pairs of settings are ordered.  So, if i is <frozen=3, framerate=3> and j
//     is <frozen=2, framerate=2>, it's not clear which will induce a bigger impact on the schedule cost.
//     Hence, one may find that !(i>j) and !(j>i), even if !(i==j) 
bool more_schedule_expensive(const ScheduleUnit &i, const ScheduleUnit &j)
{
  // This logic ensures that we return true only if i is strictly more than j
  if(i.GetNumFrozen() < j.GetNumFrozen())
    return (i.GetFPS() >= j.GetFPS());
  if(i.GetFPS() > j.GetFPS())
    return (i.GetNumFrozen() <= j.GetNumFrozen());

  return false;
}

bool less_schedule_expensive(const ScheduleUnit &i, const ScheduleUnit &j)
{
  // This logic ensures that we return true only if i is strictly less than j
  if(i.GetNumFrozen() > j.GetNumFrozen())
    return (i.GetFPS() <= j.GetFPS());
  if(i.GetFPS() < j.GetFPS())
    return (i.GetNumFrozen() >= j.GetNumFrozen());

  return false;
}

typedef unordered_map<string, AppId> AppMap; // associate app names with ids

// Data structure, indexed by app_num, where each element is an AppSettingsVec; 
typedef vector< AppSettingsVec > AppsetConfigsVov; // vector of vectors

// Parse input files
void parse_configurations_file(const string configurations_file,
			       AppMap &app_map, AppsetConfigsVov &appset_settings)
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
    AppId app_id;

    // find the app_id for this setting
    if (app_map.find(app_name) == app_map.end()) {
      // "allocate" new app id for this name
      app_id = appset_settings.size();
      app_map[app_name] = app_id;
      AppSettingsVec tmp={};
      appset_settings.push_back(tmp);
    } else {
      app_id = app_map[app_name];
    }

    // form the app setting
    ScheduleUnit unit = ScheduleUnit(app_id, num_frozen, fps, cost, metric);
    
    // add the setting to the app
    vector<ScheduleUnit> &units = appset_settings[app_id];
    units.push_back(unit);
  }

  // sort the settings vectors -- may help with pruning
  for(auto &v : appset_settings)
    std::sort(v.begin(), v.end(), less_schedule_expensive);
  
  if(debug) {
    cout << "DEBUG: === List of App Settings === " << std::endl;
    for(auto &a : app_map) {
      AppId id = a.second;
      cout << a.first << " settings: ";
      for(auto &u : appset_settings[id]) {
	cout << u << " ";
      }
      cout << std::endl;
    }
    cout << std::endl;
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

  if(budget_override != 0.0) budget = budget_override;
  
  return budget;
}

// For a given schedule-configuration, get the optimal schedule
shared_ptr<Schedule>
get_optimal_schedule(const AppsetConfigsVov appset_settings, const vector<double> layer_costs,
		     double budget, bool prune)
{
  AppId n;
  
  AppId num_apps = appset_settings.size();
    
  // schedule currently under consideration -- we assume an index for each of the possible settings
  //   for each of the app_ids
  vector<unsigned> config(num_apps, 0);
  // for(n=0; n<num_apps; n++)  config.push_back(0);   // intialize config
  
  double min_metric = numeric_limits<double>::infinity();
  shared_ptr<Schedule> best_schedule = make_shared<Schedule>(layer_costs, budget);
  unsigned long long int config_count = 0;
  unsigned long long int num_pruned = 0;

  bool done = false;
  bool overbudget;
  while (!done) {
    shared_ptr<Schedule> schedule = make_shared<Schedule>(layer_costs, budget);

    schedule->clear_apps();
    for (n=0; n<num_apps; n++) {
      // TODO: Restructure Schedule so that we pass in 'config' and 'appset_settings' 
      //   (by const reference) rather than building a new vector each time
      int app_setting_index = config[n];
      ScheduleUnit unit = appset_settings[n][app_setting_index];
      schedule->AddApp(unit);
    }

    double cost = schedule->GetCost();
    overbudget = ( cost > budget );
    double average_metric = schedule->GetAverageMetric();

    if ((average_metric < min_metric) && !overbudget) { // cost < budget){
      min_metric = average_metric;
      best_schedule = schedule;
      if (debug) {
        cout << "DEBUG: New best.  metric=" << min_metric << " cost=" << schedule->GetCost()
	     << " schedule= " << (*schedule) << std::endl;
      }
    }

    // "Increment" config
    done = true; // assume for now
    for (n=0; n<num_apps; n++) {
      int num_options = appset_settings[n].size();
      int next_option_index = config[n] + 1;
      if( overbudget && prune ) {
	while( ( next_option_index < num_options )
	      && more_schedule_expensive(appset_settings[n][next_option_index], appset_settings[n][config[n]])) {
	  ++ next_option_index;
	  // compute the number of configurations skipped by pruning this setting
	  unsigned long long int skipped = 1;
	  for(int i=0; i<n; i++)
	    skipped *= appset_settings[i].size();
	  num_pruned += skipped;
	  // TODO: Pruning could be even better if we kept track of settings known to be too expensive
	}
      }
      if (next_option_index < num_options) {
	config[n] = next_option_index;
	done = false; // found untried config
	break;
      }	
      config[n] = 0;
    }

    if ((config_count % 10000000 == 0) && (config_count != 0)) {
      cout << "Config count: " << config_count ;
      if(prune) cout << "  (" << num_pruned << " pruned)";
      if(debug) cout << "  current schedule: " << schedule;
      cout << std::endl;
    }

    ++config_count;
  }

  cout << "Final config count: " << config_count ;
  if(prune) cout << "  (" << num_pruned << " pruned)";
  cout << std::endl;

  return best_schedule;
}

void run(string data_dir, string pointer_suffix, bool prune)
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

    AppMap app_map;
    AppsetConfigsVov app_settings;
    parse_configurations_file(configurations_file, app_map, app_settings);

    vector<double> layer_costs = parse_model_file(model_file);
    double budget = parse_environment_file(environment_file);

    auto start = chrono::high_resolution_clock::now();

    shared_ptr<Schedule> sched = get_optimal_schedule(app_settings,
                                                      layer_costs,
                                                      budget,
						      prune);

    auto elapsed = chrono::high_resolution_clock::now() - start;
    long microseconds = chrono::duration_cast<std::chrono::microseconds>(elapsed).count();

    cout << (*sched) << "\n";

    outfile << sched->GetOutputLine() << "," << microseconds << "\n";

    outfile.flush();
  }

  outfile.close();
}

void usage(char *progname)
{
  cerr << "usage: " << progname << " [--debug] [--prune] [--override_budget <double>] <setup suffix> <directory>\n";
  exit(-1);
}

int main(int argc, char *argv[])
{
  bool prune = false;
  
  // parse command line
  int i = 1;
  while((i < argc) && (*argv[i] == '-') && (*argv[i+1] == '-')) {
    if(string(argv[i]) == "--debug") {
      debug = true;
    } else if(string(argv[i]) == "--prune") {
      prune = true;
    } else if(string(argv[i]) == "--override_budget") {
      budget_override = strtod(argv[++i], NULL);
      cout << "Budget override set to " << budget_override << std::endl;
    } else {
      usage(argv[0]);
    }
    ++i;
  }
  if(argc != (i+2))
    usage(argv[0]);
  string data_dir = argv[i];
  string setup_suffix = argv[++i];
  
  cout << setup_suffix << ", " << data_dir << "\n";
  run(data_dir, setup_suffix, prune);
}
