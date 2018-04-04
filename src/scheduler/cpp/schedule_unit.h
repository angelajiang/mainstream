#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

#include <iostream>

using namespace std;

typedef unsigned int AppId; // each app will have a unique id

class AppConfig {
 protected:
  int num_frozen_;
  int fps_;
 public:
 AppConfig(int num_frozen, int fps) : num_frozen_(num_frozen), fps_(fps) {}
  ~AppConfig(void) {}

  int GetNumFrozen(void) const {return num_frozen_;}
  
  int GetFPS(void) const {return fps_;}
};

// Return true if first is "lexically less than" second
// Enable sorting list of AppConfig instances
//   sort first by NumFrozen then by FPS
//   NOTE1: The first element in such a list will be the cheapest, the last will be the most expensive
//   NOTE2: Elements between first and last are ***NOT*** strictly increasing in expensiveness
//   NOTE3: "Expensiveness" increases with increasing GPS but decreases with increasing NumFrozen
inline bool lexical_lessthan(const AppConfig &first, const AppConfig &second) {
  if(first.GetNumFrozen() > second.GetNumFrozen())
    return true;
  if(first.GetNumFrozen() < second.GetNumFrozen())
    return false;
  // else  (first.GetNumFrozen() == second.GetNumFrozen())
  return (first.GetFPS() < second.GetFPS());
}
     
class ScheduleUnit : public AppConfig {
 private:
  AppId app_id_;
  double metric_;
  double branch_cost_;
  
 public:  
 ScheduleUnit(AppId app_id, int num_frozen, int fps, double branch_cost, double metric)
   : AppConfig(num_frozen, fps), app_id_(app_id), metric_(metric), branch_cost_(branch_cost)
  {}
  
  ~ScheduleUnit(void) {};
    
  AppId GetAppId(void) const {return app_id_;}
  
  double GetMetric(void) const {return metric_;}
  
  double GetBranchCost(void) const {return branch_cost_;}
};

ostream& operator<<(ostream& os, const ScheduleUnit& unit);

#endif
