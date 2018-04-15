#include <algorithm>
#include <cassert>
#include <memory>
#include <vector>
#include <sstream>
#include "schedule_unit.h"
#include "shared_stem.h"

SharedStem::SharedStem(
  const std::vector<int>& chokepoints,
  const std::vector<int>& fpses,
  std::shared_ptr<const layer_costs_t> layer_costs_subset_sums) :
  chokepoints_(chokepoints),
  fpses_(fpses),
  layer_costs_subset_sums_(layer_costs_subset_sums) {
  assert(chokepoints.size() == fpses.size());
  // Chokepoints should be strictly increasing.
  assert(std::is_sorted(chokepoints.begin(), chokepoints.end(),
                        std::less_equal<int>()));
  // FPS should be strictly decreasing.
  // (Yes, less_equal is confusing but correct.)
  assert(std::is_sorted(fpses.rbegin(), fpses.rend(),
                        std::less_equal<int>()));
  shared_cost_ = ComputeCost();
}

bool SharedStem::Allows(const ScheduleUnit& unit) const {
  // TODO(wonglkd): Replace with binary search.
  int i = 0;
  while (i < chokepoints_.size() && chokepoints_[i] < unit.GetNumFrozen()) {
    i++;
  }
  if (i >= chokepoints_.size()) {
    return false;
  }
  return fpses_[i] >= unit.GetFPS();
}

cost_t SharedStem::ComputeCost() const {
  int prev_idx = 0;
  double curr_sum = 0;
  const layer_costs_t& layer_cost_ss = *layer_costs_subset_sums_;
  for (int i = 0; i < chokepoints_.size(); ++i) {
    curr_sum += (layer_cost_ss[chokepoints_[i]] -
                 layer_cost_ss[prev_idx]) * fpses_[i];
    prev_idx = chokepoints_[i];
  }
  return curr_sum;
}

std::string SharedStem::GetString() const {
  std::stringstream ss;
  ss << "Stem([";
  for (int i = 0; i < chokepoints_.size(); ++i) {
    ss << "(" << chokepoints_[i] << ", " << fpses_[i] << ")";
    if (i != chokepoints_.size() - 1) {
      ss << ", ";
    }
  }
  ss << "], cost=" << shared_cost_ << ")";
  return ss.str();
}

std::ostream& operator<<(std::ostream& os, const SharedStem& obj) {
  return os << obj.GetString();
}
