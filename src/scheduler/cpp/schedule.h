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

    AppsetConfigsVov app_settings_;
    AppMap app_map_;
    vector<unsigned> config_;
    double budget_;
    double metric_;
    double cost_;
    
  public:

    Schedule(const AppsetConfigsVov &app_settings, const AppMap &app_map, const vector<unsigned> &config,
	     double budget, double metric, double cost)
      : app_settings_(app_settings), app_map_(app_map), config_(config), budget_(budget), metric_(metric), cost_(cost) {}

    ~Schedule(void) {};

    unsigned GetNumApps(void) const {return app_map_.size();}
    
    double GetCost(void) const {return cost_;}

    double GetBudget(void) const {return budget_;}

    double GetAverageMetric(void) const {return metric_;}

    string GetNumFrozenString(void) const;

    string GetFPSString(void) const;

    string GetOutputLine(void) const;

};

ostream& operator<<(ostream&, const Schedule&);

#endif
