#include "result.h"
#include "result_curve.h"

// Preserves sorted invariant as it adds.
void ResultCurve::Add(Result result) {
  auto after = results_set_.lower_bound(result);
  // Insertion will be at the correct place by F1.
  // If a later point (higher F1) has lower cost, we should not insert.
  if (after == results_set_.end() || F_MORE(after->GetCost(), result.GetCost())) {
    auto kv = results_set_.insert(result);
    // cerr << "Real: " << std::distance(results_set_.begin(), kv.first) / (double)results_set_.size() << ' ' << std::distance(results_set_.begin(), kv.first) << '/' << results_set_.size() << endl;
    assert(kv.second);
    dirty_ = true;

    // Once inserted, all preceding points (lower F1) with higher cost will
    // be suboptimal and can be removed.
    auto before = kv.first;
    while (before != results_set_.begin()) {
      --before;
      cost_t before_cost = before->GetCost();
      if (F_LESS(before_cost, result.GetCost())) {
        ++before;
        break;
      }
    }
    if (before != kv.first) {
      results_set_.erase(before, kv.first);
    }
  }
}

void ResultCurve::Finalize() {
  if (results_set_.size() > 0) {
    results_.reserve(results_set_.size());
    for (const auto& i : results_set_) {
      results_.push_back(std::make_shared<Result>(i));
    }
    results_set_.clear();
    dirty_ = false;
  }
}

Result::ptr_t ResultCurve::BestResult() const {
  Result::ptr_t best = results_.back();
  best->CollectSchedule();
  return best;
}
