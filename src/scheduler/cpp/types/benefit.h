#ifndef BENEFIT_H
#define BENEFIT_H

#include <algorithm>
#include <string>
#include <sstream>
#include "utility.h"

class Benefit {
 public:
  const double sum_;
  const double min_;

  inline explicit Benefit(double val) : sum_(-val), min_(-val) {}
  inline Benefit(double sum_val, double min_val) : sum_(sum_val), min_(min_val) {}

  inline const Benefit operator+(const Benefit& rhs) const {
    return Benefit(sum_ + rhs.sum_, std::min(min_, rhs.min_));
  }

  inline bool operator==(const Benefit& rhs) const {
    return F_EQL(sum_, rhs.sum_) && F_EQL(min_, rhs.min_);
  }

  inline bool operator<(const Benefit& rhs) const {
    if (F_LESS(sum_, rhs.sum_)) {
      return true;
    }
    if (F_LESS(rhs.sum_, sum_)) {
      return false;
    }
    return F_LESS(min_, rhs.min_);
  }

  inline bool operator>(const Benefit& rhs) const {
    return rhs < *this;
  }

  std::string GetString() const;
};

std::ostream& operator<<(std::ostream& os, const Benefit& obj);

#endif // BENEFIT_H
