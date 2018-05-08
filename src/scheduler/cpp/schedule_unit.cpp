
#include "schedule_unit.h"
#include <iostream>

ostream& operator<<(ostream& os, const ScheduleUnit& unit)
{
  return os << unit.GetAppId() << ":<" << unit.GetNumFrozen() << "," << unit.GetFPS() << ">";
}

/*
ScheduleUnit::ScheduleUnit(string app_id, int num_frozen, int fps, double branch_cost, double metric){
      app_id_ = app_id;
      num_frozen_ = num_frozen;
      fps_ = fps;
      metric_ = metric;
      branch_cost_ = branch_cost;
}

string ScheduleUnit::GetAppId(){
  return app_id_;
}
int ScheduleUnit::GetNumFrozen(){
  return num_frozen_;
}

int ScheduleUnit::GetFPS(){
  return fps_;
}

double ScheduleUnit::GetMetric(){
  return metric_;
}

double ScheduleUnit::GetBranchCost(){
  return branch_cost_;
}
*/
