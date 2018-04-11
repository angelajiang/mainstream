#include "schedule_unit.h"
#include <iostream>

ScheduleUnit::ScheduleUnit(string app_id, int num_frozen, int fps, double branch_cost, double metric) {
  app_id_ = app_id;
  num_frozen_ = num_frozen;
  fps_ = fps;
  metric_ = metric;
  branch_cost_ = branch_cost;
}

string ScheduleUnit::GetAppId() const {
  return app_id_;
}

int ScheduleUnit::GetNumFrozen() const {
  return num_frozen_;
}

int ScheduleUnit::GetFPS() const {
  return fps_;
}

double ScheduleUnit::GetMetric() const {
  return metric_;
}

double ScheduleUnit::GetBranchCost() const {
  return branch_cost_;
}
