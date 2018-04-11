#include <algorithm>
#include <cassert>
#include <chrono>
#include <functional>
#include <limits>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>
#include "./data.h"
#include "./schedule_unit.h"
#include "./schedule.h"

typedef std::unordered_map<std::string, std::vector<ScheduleUnit>>
    app_configs_t;
// pair<avg_f1, min_f1>
typedef std::vector<double> layer_costs_t;
typedef double cost_t;
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define EPSILON 1e-5
#define F_LESS(a, b) ((b) - (a) > EPSILON)
#define F_MORE(a, b) ((a) - (b) > EPSILON)
#define F_EQL(a, b) (!F_LESS((a), (b)) && !F_MORE((a), (b)))

class Benefit {
 public:
  const double avg_;
  const double min_;

  explicit Benefit(double val) : avg_(-val), min_(-val) {}
  Benefit(double avg_val, double min_val) : avg_(avg_val), min_(min_val) {}

  const Benefit operator+(const Benefit& rhs) const {
    return Benefit(avg_ + rhs.avg_, MIN(min_, rhs.min_));
  }

  bool operator==(const Benefit& rhs) const {
    return F_EQL(avg_, rhs.avg_) && F_EQL(min_, rhs.min_);
  }

  bool operator<(const Benefit& rhs) const {
    if (F_LESS(avg_, rhs.avg_)) {
      return true;
    }
    if (F_LESS(rhs.avg_, avg_)) {
      return false;
    }
    return F_LESS(min_, rhs.min_);
  }

  bool operator>(const Benefit& rhs) const {
    return rhs < *this;
  }
};

// bool operator==(const Benefit& lhs, const Benefit& rhs) {
//   return F_EQL(lhs.avg_, rhs.avg_) && F_EQL(lhs.min_, rhs.min_);
// }

// bool operator<(const Benefit& lhs, const Benefit& rhs) {
//   if (F_LESS(lhs.avg_, rhs.avg_)) {
//     return true;
//   }
//   if (F_LESS(rhs.avg_, lhs.avg_)) {
//     return false;
//   }
//   return F_LESS(lhs.min_, rhs.min_);
// }



// typedef Benefit benefit_t;
// typedef std::pair<double, double> benefit_t;


// inline benefit_t benefit_init(double benefit) {
//   return std::make_pair(-benefit, -benefit);
// }

// inline benefit_t benefit_agg(benefit_t a, benefit_t b) {
//   return std::make_pair(a.first + b.second, min(a.second, b.second));
// }

// inline bool benefit_lt(benefit_t a, benefit_t b) {
//   if (F_LESS(a.first, b.first)) {
//     return true;
//   }
//   return F_LESS(a.second, b.second);
// }

class SharedStem {
 private:
    const std::vector<int> chokepoints_;
    const std::vector<int> fpses_;
    std::shared_ptr<const layer_costs_t> layer_costs_subset_sums_;
    cost_t shared_cost_;

 public:
    SharedStem(const std::vector<int>& chokepoints,
               const std::vector<int>& fpses,
               std::shared_ptr<const layer_costs_t> layer_costs_subset_sums) :
               chokepoints_(chokepoints),
               fpses_(fpses),
               layer_costs_subset_sums_(layer_costs_subset_sums) {
      assert(chokepoints.size() == fpses.size());
      // Chokepoints should be strictly increasing.
      assert(std::is_sorted(chokepoints.begin(), chokepoints.end()));
      // FPS should be strictly decreasing.
      // (Yes, less_equal is confusing but correct.)
      assert(std::is_sorted(fpses.rbegin(), fpses.rend(),
                            std::less_equal<int>()));
      shared_cost_ = ComputeCost();
    }

    cost_t GetCost() const {
      return shared_cost_;
    }

    cost_t ComputeCost() const {
      // TODO(wonglkd): Compute once and store.
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

    bool operator==(const SharedStem& other) {
      return chokepoints_ == other.chokepoints_ && fpses_ == other.fpses_;
    }

    std::string GetString() const {
      std::stringstream ss;
      ss << "Stem([";
      for (int i = 0; i < chokepoints_.size(); ++i) {
        ss << "(" << chokepoints_[i] << ", " << fpses_[i] << ")";
      }
      ss << "], cost=" << shared_cost_ << ")";
      return ss.str();
    }
};

std::ostream& operator<<(std::ostream& os, SharedStem& obj) {
  return os << obj.GetString();
}


class Result {
 private:
  const Benefit benefit_;
  const cost_t cost_;
  const ScheduleUnit unit_;
  std::vector<ScheduleUnit> schedule_;
  // std::shared_ptr<Result> prev_;

 public:
  explicit Result(const ScheduleUnit& first_unit, cost_t stem_cost) :
    benefit_(Benefit(first_unit.GetMetric())),
    cost_(first_unit.GetBranchCost() + stem_cost),
    unit_(first_unit) {}

  Result(const ScheduleUnit& new_unit,
    const Result& existing) :
    benefit_(existing.GetBenefit() + Benefit(new_unit.GetMetric())),
    cost_(existing.GetCost() + new_unit.GetBranchCost()),
    unit_(new_unit),
    schedule_(existing.GetSchedule()) {
      schedule_.push_back(new_unit);
  }

  Result Relax(const ScheduleUnit& unit) const {
    return Result(unit, *this);
  }

  cost_t GetCost() const {
    return cost_;
  }

  const Benefit& GetBenefit() const {
    return benefit_;
  }

  const std::vector<ScheduleUnit>& GetSchedule() const {
    return schedule_;
  }

  // std::shared_ptr<std::vector<ScheduleUnit>> GetSchedule() const {
  //   std::vector<ScheduleUnit> schedule;
  // }

  bool operator==(const Result &other) const {
    return benefit_ == other.GetBenefit() && F_EQL(cost_, other.GetCost());
  }

  bool operator>(const Result &other) const {
    if (benefit_ == other.GetBenefit()) {
      return F_LESS(cost_, other.cost_);
    }
    return benefit_ > other.GetBenefit();
  }

  bool operator<(const Result &other) const {
    return other > *this;
  }
};


class ResultCurve {
 private:
  // TODO(wonglkd): replace with multiset?
  using results_t = std::vector<Result>;
  results_t results_;

 public:
  using iterator = results_t::iterator;
  using const_iterator = results_t::const_iterator;

  // // Preserves sorted invariant as it adds.
  // void Add(const Result& result) {
  //   // TODO(wonglkd): preserve sorted invariant here?
  // }

  void Add(Result result) {
    results_.push_back(result);
  }

  void Finalize() {
    std::set<Result> tmp;
    for (const Result& i : results_) {
      tmp.insert(i);
    }

    cost_t best_so_far = numeric_limits<cost_t>::min();

    std::vector<Result> ret_monotonic;

    for (auto ii = tmp.rbegin(); ii != tmp.rend(); ++ii) {
      if (F_LESS(ii->GetCost(), best_so_far)) {
        ret_monotonic.push_back(*ii);
        best_so_far = ii->GetCost();
      }
    }
  }

  Result BestResult() const {
    return *--results_.end();
  }

  iterator begin() {
    return results_.begin();
  }

  const_iterator begin() const {
    return results_.begin();
  }

  iterator end() {
    return results_.end();
  }

  const_iterator end() const {
    return results_.end();
  }
};

ResultCurve get_pareto_curve(
  const SharedStem& stem,
  double budget,
  app_configs_t possible_app_configs,
  std::vector<std::string> app_ids) {
  std::vector<ResultCurve> dp;
  for (std::string& app_id : app_ids) {
    ResultCurve results;

    // TODO(wonglkd): prune possible_app_configs to those that are optimal.
    if (dp.size() == 0) {
      for (const ScheduleUnit& app_config_unit : possible_app_configs[app_id]) {
        results.Add(Result(app_config_unit, stem.GetCost()));
      }
    } else {
      for (const Result& partial_result : dp[dp.size() - 1]) {
        for (const ScheduleUnit& unit : possible_app_configs[app_id]) {
          Result new_result = partial_result.Relax(unit);
          // Prune configurations that are over budget.
          if (!F_MORE(new_result.GetCost(), budget)) {
            results.Add(new_result);
          }
        }
      }
    }
    results.Finalize();
    dp.push_back(results);
  }
  return dp[dp.size() - 1];
}


std::shared_ptr<Schedule> get_optimal_schedule(
  app_configs_t possible_configurations,
  layer_costs_t layer_costs,
  double budget,
  int verbose) {
  // Enumerate through stems.

  // Initialise FPSes, chokepoints and max_steps.
  std::set<int> fps_options;
  std::set<int> chokepoints;
  for (const auto& kv : possible_configurations) {
    for (const auto& unit : kv.second) {
        fps_options.insert(unit.GetFPS());
        chokepoints.insert(unit.GetNumFrozen());
      }
  }
  int max_steps = min(possible_configurations.size(),
                      min(chokepoints.size(), fps_options.size()));


  // std::vector<int> fps_options = {1, 2, 3, 4, 5};
  // std::vector<int> chokepoints = {3, 33, 50, 81};
  // int max_steps = 4;

  // assert(std::is_sorted(fps_options.begin(), fps_options.end()));
  // assert(std::is_sorted(chokepoints.begin(), fps_options.end()));

  layer_costs_t layer_costs_subset_sums = {0};
  layer_costs_subset_sums.reserve(1 + layer_costs.size());
  double curr_sum = 0;
  for (const double& cost : layer_costs) {
    curr_sum += cost;
    layer_costs_subset_sums.push_back(curr_sum);
  }

  std::vector<std::string> app_ids;
  for (const auto& kv : possible_configurations) {
    app_ids.push_back(kv.first);
  }
  std::sort(app_ids.begin(), app_ids.end());

  std::unique_ptr<const Result> solution = nullptr;

  // Naive: try all stems.
  for (int num_steps = 0; num_steps < max_steps; ++num_steps) {
    // Try all combinations of FPSes.
    std::vector<bool> fps_sel(fps_options.size());
    std::fill(fps_sel.begin(), fps_sel.begin() + num_steps, true);
    do {
      std::vector<int> chosen_fpses;
      // Give FPSes in decreasing order.
      auto fps_opt = --fps_options.end();
      for (int i = fps_options.size() - 1; i >= 0; --i, --fps_opt) {
        if (fps_sel[i]) {
          chosen_fpses.push_back(*fps_opt);
        }
      }

      // Try all combinations of chokepoints;
      std::vector<bool> chokepoint_sels(chokepoints.size());
      std::fill(chokepoint_sels.begin(), chokepoint_sels.begin() + num_steps,
                true);
      do {
        std::vector<int> chosen_chokepoints;
        auto cp_opt = chokepoints.begin();
        for (size_t i = 0; i < chokepoints.size(); ++i, ++cp_opt) {
          if (chokepoint_sels[i]) {
            chosen_chokepoints.push_back(*cp_opt);
          }
        }

        SharedStem stem(chosen_chokepoints, chosen_fpses,
          std::make_shared<const vector<double>>(layer_costs_subset_sums));
        const Result result = get_pareto_curve(stem,
                                               budget,
                                               possible_configurations,
                                               app_ids).BestResult();
        if (solution == nullptr || *solution < result) {
          solution = std::make_unique<const Result>(result);
        }
      } while (std::prev_permutation(chokepoint_sels.begin(),
                                     chokepoint_sels.end()));
    } while (std::prev_permutation(fps_sel.begin(), fps_sel.end()));
  }

  assert(solution != nullptr);
  assert(solution->GetSchedule().size() == possible_configurations.size());

  return make_shared<Schedule>(layer_costs, budget, solution->GetSchedule());
}

void run(const std::string& data_dir,
         const std::string& pointer_suffix,
         bool debug) {
  std::string pointers_file = data_dir + "/pointers." + pointer_suffix;
  std::ifstream infile(pointers_file);

  std::string results_file =
      data_dir + "/schedules/stems_cpp.sim." + pointer_suffix;
  std::ofstream outfile(results_file);

  std::string id;

  while (infile >> id) {
    std::string configurations_file = data_dir + "/setup/configuration." + id;
    std::string model_file = data_dir + "/setup/model." + id;
    std::string environment_file = data_dir + "/setup/environment." + id;

    std::cout << "Getting optimal schedule for config " << id << "\n"
              << std::flush;

    app_configs_t possible_configurations =
      parse_configurations_file(configurations_file);

    layer_costs_t layer_costs = parse_model_file(model_file);
    double budget = parse_environment_file(environment_file);

    auto start = chrono::high_resolution_clock::now();

    std::shared_ptr<Schedule> sched = get_optimal_schedule(possible_configurations,
                                                      layer_costs,
                                                      budget,
                                                      debug);

    auto elapsed = chrono::high_resolution_clock::now() - start;
    auto microseconds =
        chrono::duration_cast<std::chrono::microseconds>(elapsed).count();

    cout << (*sched) << "\n";

    outfile << sched->GetOutputLine() << "," << microseconds << "\n";

    outfile.flush();
  }

  outfile.close();
}

int main(int argc, char *argv[]) {
  string data_dir = argv[1];
  string setup_suffix = argv[2];
  bool debug = true;
  cout << setup_suffix << ", " << data_dir << "\n";
  run(data_dir, setup_suffix, debug);
  return 0;
}
