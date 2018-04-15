#include "schedule_unit.h"
#include "utility.h"
#include <iostream>
#include <sstream>
#include <string>


ScheduleUnit::ScheduleUnit(std::string app_id, int num_frozen, int fps, double branch_cost, double metric) {
  app_id_ = app_id;
  num_frozen_ = num_frozen;
  fps_ = fps;
  metric_ = metric;
  branch_cost_ = branch_cost;
}

std::string ScheduleUnit::GetAppId() const {
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

std::string ScheduleUnit::GetString() const {
  std::stringstream ss;
  ss << "(" << num_frozen_ << "," << fps_ << ")";
  return ss.str();
}

// Lowest/best metric first, then increasing cost
bool ScheduleUnit::operator<(const ScheduleUnit& rhs) const {
  if (F_EQL(metric_, rhs.GetMetric())) {
    return F_LESS(branch_cost_, rhs.GetBranchCost());
  }
  return F_LESS(metric_, rhs.GetMetric());
}

std::ostream& operator<<(std::ostream& os, const ScheduleUnit& obj) {
  return os << obj.GetString();
}
