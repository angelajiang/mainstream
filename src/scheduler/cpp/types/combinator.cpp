#include "combinator.h"

void Combinator::resetOuter() {
  fps_sels_.assign(fps_options_.size(), false);
  std::fill(fps_sels_.begin(), fps_sels_.begin() + num_steps_, true);
}

void Combinator::resetInner() {
  chokepoint_sels_.assign(chokepoints_.size(), false);
  std::fill(chokepoint_sels_.begin(), chokepoint_sels_.begin() + num_steps_,
            true);
}

bool Combinator::advanceOuter() {
  return std::prev_permutation(fps_sels_.begin(), fps_sels_.end());
}

bool Combinator::advanceInner() {
  return std::prev_permutation(chokepoint_sels_.begin(),
                               chokepoint_sels_.end());
}

Combinator::Combinator(const std::set<int>& fps_options,
                       const std::set<int>& chokepoints,
                       int num_steps) :
    fps_options_(fps_options),
    chokepoints_(chokepoints),
    num_steps_(num_steps) {
  resetOuter();
  resetInner();
}

int Combinator::Next() {
  if (advanceInner()) {
    return 2;
  } else if (advanceOuter()) {
    resetInner();
    return 1;
  } else {
    return -1;
  }
}

std::vector<int> Combinator::FPSes() const {
  std::vector<int> chosen_fpses;
  // Give FPSes in decreasing order.
  auto fps_opt = --fps_options_.end();
  for (int i = fps_options_.size() - 1; i >= 0; --i, --fps_opt) {
    if (fps_sels_[i]) {
      chosen_fpses.push_back(*fps_opt);
    }
  }
  assert(chosen_fpses.size() == num_steps_);
  return chosen_fpses;
}

std::vector<int> Combinator::Chokepoints() const {
  std::vector<int> chosen_chokepoints;
  auto cp_opt = chokepoints_.begin();
  for (size_t i = 0; i < chokepoints_.size(); ++i, ++cp_opt) {
    if (chokepoint_sels_[i]) {
      chosen_chokepoints.push_back(*cp_opt);
    }
  }
  assert(chosen_chokepoints.size() == num_steps_);
  return chosen_chokepoints;
}
