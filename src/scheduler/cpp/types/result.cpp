#include "result.h"
#include <list>
#include <string>
#include <sstream>

Result::Result(const ScheduleUnit& first_unit, cost_t stem_cost) :
  benefit_(Benefit(first_unit.GetMetric())),
  cost_(first_unit.GetBranchCost() + stem_cost),
  unit_(first_unit) {}

Result::Result(const ScheduleUnit& new_unit, ptr_t existing) :
  benefit_(existing->GetBenefit() + Benefit(new_unit.GetMetric())),
  cost_(existing->GetCost() + new_unit.GetBranchCost()),
  unit_(new_unit),
  prev_(existing) {}

Result::Result(const ScheduleUnit& new_unit, ptr_t existing, cost_t stem_cost) :
  benefit_(existing->GetBenefit() + Benefit(new_unit.GetMetric())),
  cost_(existing->GetCost() + new_unit.GetBranchCost() + stem_cost),
  unit_(new_unit),
  prev_(existing) {}


void Result::CollectSchedule() {
  if (prev_ != nullptr) {
    std::list<ScheduleUnit> schedule_list = {unit_};
    while (prev_ != nullptr) {
      schedule_list.push_front(prev_->unit_);
      prev_ = prev_->prev_;
    }
    schedule_.assign(schedule_list.begin(), schedule_list.end());
  } else if (schedule_.size() == 0) {
    schedule_.push_back(unit_);
  }
}

std::string Result::GetString() const {
  std::stringstream ss;
  ss << "Result(cost=" << cost_ << ", benefit=" << benefit_;
  ss << ", schedule=[";
  for (const ScheduleUnit& unit : schedule_) {
    ss << unit << ",";
  }
  ss << "]";
  ss << ")";
  return ss.str();
}

std::ostream& operator<<(std::ostream& os, const Result& obj) {
  return os << obj.GetString();
}
