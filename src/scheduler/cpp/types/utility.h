#ifndef UTILITY_H
#define UTILITY_H

#include <cmath>
#include <string>
#include <vector>
#include <unordered_map>
#include "schedule_unit.h"

// EPSILON needs to be a few orders of magnitude smaller than output precision
// since F1s are typically divided by num of apps.
#define EPSILON 1e-8
#define F_LESS(a, b) ((b) - (a) > EPSILON)
#define F_MORE(a, b) ((a) - (b) > EPSILON)
#define F_EQL(a, b) (fabs((a)-(b)) <= EPSILON)


typedef std::unordered_map<std::string, std::vector<ScheduleUnit>>
    app_configs_t;
typedef std::vector<double> layer_costs_t;
typedef double cost_t;

template<typename T>
inline std::vector<T> get_subset_sums(const std::vector<T>& vals) {
  std::vector<T> subset_sums = {0};
  subset_sums.reserve(1 + vals.size());
  T curr_sum = 0;
  for (const T& val : vals) {
    curr_sum += val;
    subset_sums.push_back(curr_sum);
  }
  return subset_sums;
}

#endif // UTILITY_H
