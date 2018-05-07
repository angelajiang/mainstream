#ifndef SCHEDULE_H
#define SCHEDULE_H


#include <iostream>
#include <set>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"

using namespace std;

// Helper data struct: simple vector of possible (sharing, framerate, cost, metric) settings for an app
typedef vector<ScheduleUnit> AppSettingsVec; 

typedef unordered_map<string, AppId> AppMap; // associate app names with ids

// Data structure, indexed by app_num, where each element is an AppSettingsVec; 
typedef vector< AppSettingsVec > AppsetConfigsVov; // vector of vectors

class Schedule
{
  private: 

    // vector<ScheduleUnit> schedule_;
    // vector<double> layer_costs_;

    AppsetConfigsVov appset_settings_;
    AppMap app_map_;
    vector<unsigned> config_;
    double budget_;
    double metric_;

  public:

    // Schedule(vector<double>, double budget);

    Schedule(const AppsetConfigsVov &appset_settings, const AppMap &app_map, const vector<unsigned> &config, double budget, double metric)
      : appset_settings_(), app_map_(app_map), config_(config), budget_(budget), metric_(metric) {}

    ~Schedule() {};

    // void AddApp(ScheduleUnit);

    // double GetCost();

    // double GetBudget();

    // set<int> GetBranchPoints();

    // pair<vector<int>, vector<int>> GetAppsBranchedFPS(int);

    // void clear_apps(void);

    double GetAverageMetric();

    string GetNumFrozenString();

    string GetFPSString();

    string GetPrintStatement();

    string GetOutputLine();

};

// ostream& operator<<(ostream&, Schedule&);

#endif
