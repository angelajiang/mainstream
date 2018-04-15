#ifndef RESULT_CURVE_H
#define RESULT_CURVE_H

#include <set>
#include "result.h"

class ResultCurve {
 private:
  using results_t = std::vector<Result::ptr_t>;
  results_t results_;
  std::set<Result> results_set_;

 public:
  using iterator = results_t::iterator;
  using const_iterator = results_t::const_iterator;

  // Preserves sorted invariant as it adds.
  void Add(Result result);

  void Finalize();

  Result::ptr_t BestResult() const;

  void assign(const ResultCurve& rhs) {
    results_set_.clear();
    results_.assign(rhs.begin(), rhs.end());
  }

  inline iterator begin() {
    return results_.begin();
  }

  inline const_iterator begin() const {
    return results_.begin();
  }

  inline iterator end() {
    return results_.end();
  }

  inline const_iterator end() const {
    return results_.end();
  }

  inline size_t size() const {
    return results_.size();
  }
};


#endif // RESULT_CURVE_H


