#ifndef COMBINATOR_H
#define COMBINATOR_H

#include <algorithm>
#include <cassert>
#include <set>
#include <vector>

class Combinator {
 private:
  const std::set<int> fps_options_;
  const std::set<int> chokepoints_;
  const int num_steps_;
  std::vector<bool> fps_sels_;
  std::vector<bool> chokepoint_sels_;

  void resetOuter();
  void resetInner();
  bool advanceOuter();
  bool advanceInner();

 public:
  Combinator(const std::set<int>& fps_options,
             const std::set<int>& chokepoints,
             int num_steps);
  int Next();
  std::vector<int> FPSes() const;
  std::vector<int> Chokepoints() const;
};

#endif  // COMBINATOR_H
