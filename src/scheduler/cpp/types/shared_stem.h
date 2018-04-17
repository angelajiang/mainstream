#ifndef SHARED_STEM_H
#define SHARED_STEM_H

#include <string>
#include <vector>
#include "utility.h"

class SharedStem {
 private:
    const std::vector<int> chokepoints_;
    const std::vector<int> fpses_;
    std::shared_ptr<const layer_costs_t> layer_costs_subset_sums_;
    cost_t shared_cost_;

 public:
    SharedStem(const std::vector<int>& chokepoints,
               const std::vector<int>& fpses,
               std::shared_ptr<const layer_costs_t> layer_costs_subset_sums);

    bool Allows(const ScheduleUnit& unit) const;

    inline cost_t GetCost() const {
      return shared_cost_;
    }

    cost_t ComputeCost() const;

    std::string GetString() const;

    inline bool operator==(const SharedStem& other) {
      return chokepoints_ == other.chokepoints_ && fpses_ == other.fpses_;
    }
};

std::ostream& operator<<(std::ostream& os, const SharedStem& obj);

#endif // SHARED_STEM_H
