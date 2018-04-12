#include <algorithm>
#include <cassert>
#include <chrono>
#include <functional>
#include <limits>
#include <list>
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
#include "./utility.h"

typedef std::unordered_map<std::string, std::vector<ScheduleUnit>>
    app_configs_t;
typedef std::vector<double> layer_costs_t;
typedef double cost_t;

class Benefit {
 public:
  const double sum_;
  const double min_;

  explicit Benefit(double val) : sum_(-val), min_(-val) {}
  Benefit(double sum_val, double min_val) : sum_(sum_val), min_(min_val) {}

  const Benefit operator+(const Benefit& rhs) const {
    return Benefit(sum_ + rhs.sum_, min(min_, rhs.min_));
  }

  bool operator==(const Benefit& rhs) const {
    return F_EQL(sum_, rhs.sum_) && F_EQL(min_, rhs.min_);
  }

  bool operator<(const Benefit& rhs) const {
    if (F_LESS(sum_, rhs.sum_)) {
      return true;
    }
    if (F_LESS(rhs.sum_, sum_)) {
      return false;
    }
    return F_LESS(min_, rhs.min_);
  }

  bool operator>(const Benefit& rhs) const {
    return rhs < *this;
  }

  std::string GetString() const {
    std::stringstream ss;
    ss << sum_;
    return ss.str();
  }
};


std::ostream& operator<<(std::ostream& os, const Benefit& obj) {
  return os << obj.GetString();
}


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

    bool Allows(const ScheduleUnit& unit) const {
      // TODO(wonglkd): Replace with binary search.
      int i = 0;
      while (i < chokepoints_.size() && chokepoints_[i] < unit.GetNumFrozen()) {
        i++;
      }
      if (i >= chokepoints_.size()) {
        return false;
      }
      return fpses_[i] >= unit.GetFPS();
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
        if (i != chokepoints_.size() - 1) {
          ss << ", ";
        }
      }
      ss << "], cost=" << shared_cost_ << ")";
      return ss.str();
    }
};

std::ostream& operator<<(std::ostream& os, const SharedStem& obj) {
  return os << obj.GetString();
}


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
  void CollectSchedule() {
    std::list<ScheduleUnit> schedule_list = {unit_};
    while (prev_ != nullptr) {
      schedule_list.push_front(prev_->unit_);
      prev_ = prev_->prev_;
    }
    schedule_.assign(schedule_list.begin(), schedule_list.end());
  }

  explicit Result(const ScheduleUnit& first_unit, cost_t stem_cost) :
    benefit_(Benefit(first_unit.GetMetric())),
    cost_(first_unit.GetBranchCost() + stem_cost),
    unit_(first_unit),
    schedule_({first_unit}) {}

  Result(const ScheduleUnit& new_unit, ptr_t existing) :
    benefit_(existing->GetBenefit() + Benefit(new_unit.GetMetric())),
    cost_(existing->GetCost() + new_unit.GetBranchCost()),
    unit_(new_unit),
    prev_(existing) {}

  cost_t GetCost() const {
    return cost_;
  }

  const Benefit& GetBenefit() const {
    return benefit_;
  }

  const std::vector<ScheduleUnit>& GetSchedule() const {
    // If this fires, we forgot to call CollectSchedule.
    assert(prev_ == nullptr);
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

  std::string GetString() const {
    std::stringstream ss;
    ss << "Result(cost=" << cost_ << ", benefit=" << benefit_;
    ss << ", schedule=[";
    for (const ScheduleUnit& unit : schedule_) {
      ss << unit << ",";
    }
    ss << "]";
    ss << ")";
    return ss.str();
  }
};

std::ostream& operator<<(std::ostream& os, const Result& obj) {
  return os << obj.GetString();
}


class ResultHandle {
 public:
  Result::ptr_t ptr_;

  explicit ResultHandle(const Result::ptr_t& ptr) : ptr_(ptr) {}

  bool operator<(const ResultHandle& rhs) const {
    return *ptr_ < *rhs.ptr_;
  }
};


class ResultCurve {
 private:
  using results_t = std::set<ResultHandle>;
  results_t results_;

 public:
  using iterator = results_t::iterator;
  using const_iterator = results_t::const_iterator;

  // Preserves sorted invariant as it adds.
  void Add(Result::ptr_t result) {
    ResultHandle rh(result);
    auto after = results_.lower_bound(rh);
    // Insertion will be at the correct place by F1.
    // If a later point (higher F1) has lower cost, we should not insert.
    if (after == results_.end() || F_MORE(after->ptr_->GetCost(), result->GetCost())) {
      auto kv = results_.insert(ResultHandle(result));
      assert(kv.second);

      // Once inserted, all preceding points (lower F1) with higher cost will
      // be suboptimal and can be removed.
      auto before = kv.first;
      while (before != results_.begin()) {
        --before;
        cost_t before_cost = before->ptr_->GetCost();
        if (F_LESS(before_cost, result->GetCost())) {
          ++before;
          break;
        }
      }
      if (before != kv.first) {
        results_.erase(before, kv.first);
      }
    }
  }

  void Finalize() {
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

  Result::ptr_t BestResult() const {
    // auto best = *std::max_element(results_.begin(), results_.end());
    auto best = *--results_.end();
    best.ptr_->CollectSchedule();
    return best.ptr_;
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

  size_t size() const {
    return results_.size();
  }
};

ResultCurve get_pareto_curve(
  const SharedStem& stem,
  double budget,
  app_configs_t possible_app_configs,
  std::vector<std::string> app_ids) {
  std::vector<ResultCurve> dp;
  // cerr << stem << endl;
  // int cnt = 0;
  for (std::string& app_id : app_ids) {
    ResultCurve results;

    // App configs allowed under stem.
    std::set<ScheduleUnit> allowed_configs;
    // TODO(wonglkd): prune possible_app_configs to those that are optimal.
    // std::cerr << "Allowed: ";
    for (const ScheduleUnit& unit : possible_app_configs[app_id]) {
      if (stem.Allows(unit)) {
        allowed_configs.insert(unit);
        // std::cerr << unit << ",";
      }
    }
    cost_t best_so_far = numeric_limits<cost_t>::infinity();
    for (auto ii = allowed_configs.begin(); ii != allowed_configs.end(); ) {
      if (F_LESS(ii->GetBranchCost(), best_so_far)) {
        ++ii;
      } else {
        ii = allowed_configs.erase(ii);
      }
    }

    if (dp.size() == 0) {
      for (const ScheduleUnit& app_config_unit : allowed_configs) {
        results.Add(std::make_shared<Result>(app_config_unit, stem.GetCost()));
      }
    } else {
      for (const auto& partial_result_handle : dp[dp.size() - 1]) {
        auto partial_result = partial_result_handle.ptr_;
        for (const ScheduleUnit& unit : allowed_configs) {
          // Result new_result = partial_result.Relax(unit);
          // Prune configurations that are over budget.
          if (!F_MORE(partial_result->GetCost() + unit.GetBranchCost(), budget)) {
            results.Add(std::make_shared<Result>(unit, partial_result));
          }
        }
      }
    }
    // cerr << "\t" << ++cnt << " " << results.size() << endl;
    results.Finalize();
    dp.push_back(results);
  }
  // if (dp[dp.size() - 1].size() > 0) {
  //   dp[dp.size() - 1].BestResult();
  // }
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

  std::shared_ptr<Result> solution = nullptr;

  int cnt_stems_total = 0;

  // Naive: try all stems.
  for (int num_steps = 1; num_steps <= max_steps; ++num_steps) {
    int cnt_stems = 0;
    int cnt_stems_in_budget = 0;
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

        cnt_stems++;

        // assert(chosen_chokepoints.size() == num_steps);
        // assert(chosen_fpses.size() == num_steps);

        SharedStem stem(chosen_chokepoints, chosen_fpses,
          std::make_shared<const vector<double>>(layer_costs_subset_sums));

        // Prune stems that exceed budget.
        if (F_MORE(stem.GetCost(), budget)) {
          continue;
        }
        cnt_stems_in_budget++;

        ResultCurve curve = get_pareto_curve(stem,
                                      budget,
                                      possible_configurations,
                                      app_ids);
        if (curve.size() > 0) {
          auto result = curve.BestResult();
          if (solution == nullptr || *solution < *result) {
            solution = result;

            std::cerr << "Improved: " << std::endl;
            std::cerr << "\t" << stem << std::endl;
            std::cerr << "\t" << *result << std::endl;
          }
        }
      } while (std::prev_permutation(chokepoint_sels.begin(),
                                     chokepoint_sels.end()));
    } while (std::prev_permutation(fps_sel.begin(), fps_sel.end()));
    cnt_stems_total += cnt_stems;
    std::cerr << num_steps << " " << cnt_stems << " " << cnt_stems_in_budget << std::endl;
  }

  std::cerr << "Total stems: " << cnt_stems_total << std::endl;

  assert(solution != nullptr);
  assert(solution->GetSchedule().size() == possible_configurations.size());
  auto schedule_ = Schedule(layer_costs, budget, solution->GetSchedule());
  std::cerr << std::endl;
  std::cerr << "Schedule: " << schedule_ << std::endl;
  std::cerr << "Stem Cost:" << schedule_.GetStemCost() << std::endl;
  std::cerr << schedule_.GetCost() << ' ' << solution->GetCost() << ' ';
  std::cerr << schedule_.GetAverageMetric() << ' ' << -(double)solution->GetBenefit().sum_ / app_ids.size() << std::endl;
  assert(F_EQL(schedule_.GetCost(), solution->GetCost()));
  assert(F_EQL(schedule_.GetAverageMetric(), -(double)solution->GetBenefit().sum_ / app_ids.size()));

  return make_shared<Schedule>(layer_costs, budget, solution->GetSchedule());
}

void run(const std::string& data_dir,
         const std::string& pointer_suffix,
         bool debug) {
  std::string pointers_file = data_dir + "/pointers." + pointer_suffix;
  std::ifstream infile(pointers_file);

  // TODO: Duplicate apps mean that C++ version can't handle (because it infers from configuration file.)
  // std::string setups_file = data_dir + "/setups." + pointer_suffix;
  // std::ifstream setupsinfile(pointers_file);

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

    std::shared_ptr<Schedule> sched = get_optimal_schedule(
      possible_configurations,
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
