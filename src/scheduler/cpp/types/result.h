#ifndef RESULT_H
#define RESULT_H

#include <cassert>
#include <memory>
#include <string>
#include <vector>
#include "benefit.h"
#include "schedule_unit.h"
#include "utility.h"

class Result {
 public:
  using ptr_t = std::shared_ptr<Result>;

 private:
  const Benefit benefit_;
  const cost_t cost_;
  const ScheduleUnit unit_;
  std::vector<ScheduleUnit> schedule_;

 protected:
  ptr_t prev_;

 public:
  Result(const ScheduleUnit& first_unit, cost_t stem_cost);

  Result(const ScheduleUnit& new_unit, ptr_t existing);

  Result(const ScheduleUnit& new_unit, ptr_t existing, cost_t stem_cost);

  inline cost_t GetCost() const {
    return cost_;
  }

  inline const Benefit& GetBenefit() const {
    return benefit_;
  }

  inline const std::vector<ScheduleUnit>& GetSchedule() const {
    // If this fires, we forgot to call CollectSchedule.
    assert(prev_ == nullptr);
    return schedule_;
  }

  void CollectSchedule();

  // std::shared_ptr<std::vector<ScheduleUnit>> GetSchedule() const {
  //   std::vector<ScheduleUnit> schedule;
  // }

  inline bool operator==(const Result &other) const {
    return benefit_ == other.GetBenefit() && F_EQL(cost_, other.GetCost());
  }

  inline bool operator>(const Result &other) const {
    if (benefit_ == other.GetBenefit()) {
      return F_LESS(cost_, other.cost_);
    }
    return benefit_ > other.GetBenefit();
  }

  inline bool operator<(const Result &other) const {
    return other > *this;
  }

  std::string GetString() const;
};

// class ResultHandle {
//  public:
//   Result::ptr_t ptr_;

//   explicit ResultHandle(const Result::ptr_t& ptr) : ptr_(ptr) {}

//   bool operator<(const ResultHandle& rhs) const {
//     return *ptr_ < *rhs.ptr_;
//   }
// };

std::ostream& operator<<(std::ostream& os, const Result& obj);

#endif // RESULT_H
