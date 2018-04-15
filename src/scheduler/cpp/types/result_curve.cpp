#include "result.h"
#include "result_curve.h"

// // Preserves sorted invariant as it adds.
// void Add(Result::ptr_t result) {
//   ResultHandle rh(result);
//   auto after = results_.lower_bound(rh);
//   // Insertion will be at the correct place by F1.
//   // If a later point (higher F1) has lower cost, we should not insert.
//   if (after == results_.end() || F_MORE(after->ptr_->GetCost(), result->GetCost())) {
//     auto kv = results_.insert(ResultHandle(result));
//     assert(kv.second);

//     // Once inserted, all preceding points (lower F1) with higher cost will
//     // be suboptimal and can be removed.
//     auto before = kv.first;
//     while (before != results_.begin()) {
//       --before;
//       cost_t before_cost = before->ptr_->GetCost();
//       if (F_LESS(before_cost, result->GetCost())) {
//         ++before;
//         break;
//       }
//     }
//     if (before != kv.first) {
//       results_.erase(before, kv.first);
//     }
//   }
// }

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
  // std::set<Result::ptr_t> tmp;
  // for (const auto& i : results_) {
  //   tmp.insert(i);
  // }

  // cost_t best_so_far = numeric_limits<cost_t>::infinity();

  // std::vector<Result> ret_monotonic;

  // for (auto ii = tmp.rbegin(); ii != tmp.rend(); ++ii) {
  //   if (F_LESS(ii->GetCost(), best_so_far)) {
  //     ret_monotonic.push_back(*ii);
  //     best_so_far = ii->GetCost();
  //   }
  // }
  // // std::cerr << "Before: ";
  // // for(auto&& i : tmp) {
  // //   std::cerr << "(" << i->GetBenefit() << "," << i->GetCost() << "),";
  // // }
  // // std::cerr << std::endl;
  // // std::cerr << "After: ";
  // // for(auto&& i : ret_monotonic) {
  // //   std::cerr << "(" << i->GetBenefit() << "," << i->GetCost() << "),";
  // // }
  // // std::cerr << std::endl;

  // results_ = std::move(ret_monotonic);
}

Result::ptr_t ResultCurve::BestResult() const {
  // auto best = *std::max_element(results_.begin(), results_.end());
  Result::ptr_t best = results_.back();
  best->CollectSchedule();
  return best;
  // if (std::max_element(results_.begin(), results_.end()) != results_.begin()) {
  //   std::cerr << "Max:" << *std::max_element(results_.begin(), results_.end()) << std::endl;
  //   std::cerr << "After: ";
  //   for (auto&& i : results_) {
  //     std::cerr << "(" << i->GetBenefit() << "," << i->GetCost() << "),";
  //   }
  //   std::cerr << std::endl;
  // }
  // assert(**std::max_element(results_.begin(), results_.end()) == **results_.begin());
  // (*results_.begin())->CollectSchedule();
  // return *results_.begin();
}
