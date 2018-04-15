#include <algorithm>
#include <cassert>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <set>
#include <stack>
#include <string>
#include <vector>
#include <utility>
#include "data.h"
#include "types/benefit.h"
#include "types/result.h"
#include "types/result_curve.h"
#include "types/schedule_unit.h"
#include "types/schedule.h"
#include "types/shared_stem.h"
#include "types/utility.h"

std::vector<ResultCurve> get_pareto_curves(
  const SharedStem& stem,
  const double budget,
  app_configs_t all_app_configs,
  const std::vector<std::string>& app_ids,
  const std::vector<ResultCurve>& dp_prev = {},
  app_configs_t delta_app_configs = {}) {
  std::vector<ResultCurve> dp;
  int app_idx = 0;
  bool dirty = false;
  for (std::string app_id : app_ids) {
    ResultCurve results;

    // App configs allowed under stem.
    // TODO: Remove since redundant (applied earlier).
    std::set<ScheduleUnit> allowed_configs;
    if (dirty || delta_app_configs.size() == 0) {
      for (const ScheduleUnit& unit : all_app_configs[app_id]) {
        assert(stem.Allows(unit));
        allowed_configs.insert(unit);
      }
    } else {
      for (const ScheduleUnit& unit : delta_app_configs[app_id]) {
        assert(stem.Allows(unit));
        allowed_configs.insert(unit);
      }
    }

    // Prune possible_app_configs to those that are optimal.
    // TODO: Remove since redundant (applied earlier).
    cost_t best_so_far = std::numeric_limits<cost_t>::infinity();
    for (auto ii = allowed_configs.begin(); ii != allowed_configs.end(); ) {
      if (F_LESS(ii->GetBranchCost(), best_so_far)) {
        best_so_far = ii->GetBranchCost();
        ++ii;
      } else {
        assert(false);
        ii = allowed_configs.erase(ii);
      }
    }

    // TODO: Optimisation: if allowed_configs is empty, just return dp_prev.
    if (dp_prev.size() > 0) {
      // assert(dp_prev.find(app_idx) != dp_prev.end());
      if (allowed_configs.size() > 0) {
        results.assign(dp_prev[app_idx]);
      } else {
        results.assign_vec(dp_prev[app_idx]);
      }
    }
    if (allowed_configs.size() > 0) {
      if (app_idx == 0) {
        for (auto ii = allowed_configs.rbegin(); ii != allowed_configs.rend(); ++ii) {
          const ScheduleUnit& app_config_unit = *ii;
          results.Add(Result(app_config_unit, 0));
        }
      } else {
        for (const auto& partial_result : dp[dp.size() - 1]) {
          for (auto ii = allowed_configs.rbegin(); ii != allowed_configs.rend(); ++ii) {
            const ScheduleUnit& unit = *ii;
            // Prune configurations that are over budget.
            if (!F_MORE(partial_result->GetCost() + unit.GetBranchCost(), budget)) {
              if (app_idx == app_ids.size() - 1) {
                results.Add(Result(unit, partial_result, stem.GetCost()));
              } else {
                results.Add(Result(unit, partial_result));
              }
            } else {
              // Since we are enumerating allowed_configs in increasing F1/weight,
              // we can break.
              break;
            }
          }
        }
      }
    }
    // cerr << "\t" << ++cnt << " " << results.size() << endl;
    // if (results.IsDirty()) {
    //   std::cerr << "dirty at " << app_idx << std::endl;
    // }
    dirty = dirty || results.IsDirty();
    results.Finalize();
    dp.push_back(results);
    app_idx++;
  }
  assert(app_ids.size() == dp.size());
  if (dp.back().size() > 0) {
    dp.back().BestResult();
  }
  return dp;
}

app_configs_t filter_configs(app_configs_t possible_configs,
                             const SharedStem& stem) {
  app_configs_t stem_app_configs;
  for (const auto& kv : possible_configs) {
    std::vector<ScheduleUnit> allowed_configs;
    for (const ScheduleUnit& unit : kv.second) {
      if (stem.Allows(unit)) {
        allowed_configs.push_back(unit);
      }
    }
    stem_app_configs[kv.first] = allowed_configs;
  }
  return stem_app_configs;
}

std::pair<app_configs_t, app_configs_t> partition_configs(
  app_configs_t possible_configs,
  const SharedStem& stem) {
  app_configs_t stem_app_configs, remaining;
  for (const auto& kv : possible_configs) {
    std::vector<ScheduleUnit> allowed_configs, remaining_local;
    for (const ScheduleUnit& unit : kv.second) {
      if (stem.Allows(unit)) {
        allowed_configs.push_back(unit);
      } else {
        remaining_local.push_back(unit);
      }
    }
    stem_app_configs[kv.first] = allowed_configs;
    remaining[kv.first] = remaining_local;
  }
  return {stem_app_configs, remaining};
}

// For each stem, filter those that don't match at the outset.
// Only supply those configs that are valid, but not under parent.
// Allow to supply a dp array, which will be used to start off.
Result::ptr_t stems_dp(
  const std::set<int>& fps_options,
  const std::set<int>& chokepoints,
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  const layer_costs_t& layer_costs_subset_sums,
  double budget,
  int verbose) {
  Result::ptr_t solution = nullptr;
  int max_steps = std::min(possible_configurations.size(),
                      std::min(chokepoints.size(), fps_options.size()));

  // FPS in descending order.
  std::vector<int> fps_options_(fps_options.rbegin(), fps_options.rend());
  std::vector<int> chokepoints_(chokepoints.begin(), chokepoints.end());

  // Stacks.
  std::vector<std::pair<int,int>> chosen_idxs;
  std::vector<int> chosen_fpses, chosen_chokepoints;
  std::vector<std::vector<ResultCurve>> dps_stack;
  std::vector<app_configs_t> remaining_configs;

  chosen_idxs.reserve(max_steps);
  chosen_fpses.reserve(max_steps);
  chosen_chokepoints.reserve(max_steps);
  dps_stack.reserve(max_steps);
  remaining_configs.reserve(max_steps);

  chosen_idxs.push_back({0, -1});
  chosen_chokepoints.push_back(-1);
  chosen_fpses.push_back(-1);
  dps_stack.push_back({});
  remaining_configs.push_back(possible_configurations);

  while (!chosen_idxs.empty()) {
    // process
    auto idxes = chosen_idxs.back();
    chosen_idxs.pop_back();
    chosen_chokepoints.pop_back();
    chosen_fpses.pop_back();
    if (idxes.first == chokepoints_.size() - 1 &&
        idxes.second == fps_options_.size() - 1) {
      dps_stack.pop_back();
      remaining_configs.pop_back();
      continue;
    } else if (idxes.second == fps_options_.size() - 1) {
      chosen_idxs.push_back({idxes.first + 1,
                             chosen_idxs.size() > 0 ? chosen_idxs.back().second + 1 : 0});
    } else {
      chosen_idxs.push_back({idxes.first, idxes.second + 1});
    }
    std::pair<int, int> curr = chosen_idxs.back();
    chosen_chokepoints.push_back(chokepoints_[curr.first]);
    chosen_fpses.push_back(fps_options_[curr.second]);

    if (verbose > 1) {
      for(auto&& kv : chosen_idxs) {
        std::cerr << "(" << kv.first << ',' << kv.second << ") ";
      }
      std::cerr << ", ";
      for(auto&& fps : chosen_fpses) {
        std::cerr << fps << ' ';
      }
      std::cerr << ", ";
      for(auto&& chokepoint : chosen_chokepoints) {
        std::cerr << chokepoint << ' ';
      }
      std::cerr << std::endl;
      std::cerr << "DP: ";
      for(auto&& dps : dps_stack) {
        for(auto&& dp : dps) {
          std::cerr << dp.size() << ", ";
        }
        std::cerr << " | ";
      }
      std::cerr << std::endl;
    }

    // Process the stem.
    assert(chosen_chokepoints.size() == chosen_idxs.size());
    assert(chosen_fpses.size() == chosen_idxs.size());
    assert(dps_stack.size() == chosen_idxs.size());
    assert(remaining_configs.size() == chosen_idxs.size());
    SharedStem stem(chosen_chokepoints, chosen_fpses,
      std::make_shared<const std::vector<double>>(layer_costs_subset_sums));

    if (verbose > 1) {
      std::cerr << stem << std::endl;
    }

    if (F_MORE(stem.GetCost(), budget)) {
      continue;
    }

    auto valid_configs = filter_configs(possible_configurations, stem);
    auto delta_new = partition_configs(remaining_configs.back(), stem);
    auto& delta_configs = delta_new.first;
    auto& remaining_configs_new = delta_new.second;
    if (verbose > 2) {
      std::cerr << remaining_configs.size() << "(" << remaining_configs.back() << ") " << delta_configs << " " << remaining_configs_new << std::endl;
    }
    std::vector<ResultCurve> curves = get_pareto_curves(stem, budget, valid_configs, app_ids, dps_stack.back(), delta_configs);
    if (verbose > 2) {
      std::cerr << curves.size() << " (";
      for(auto&& curve : curves) {
        std::cerr << curve.size() << ',';
      }
      std::cerr << ")" << std::endl;
    }
    // Relax global solution.
    if (curves.back().size() > 0) {
      auto result = curves.back().BestResult();
      if (solution == nullptr || *solution < *result) {
        solution = result;
        std::cerr << "Improved: " << std::endl;
        std::cerr << "\t" << stem << std::endl;
        std::cerr << "\t" << *result << std::endl;
      }
    }
    if (chosen_idxs.size() < max_steps &&
        curr.first + 1 < chokepoints_.size() &&
        curr.second + 1 < fps_options_.size()) {
      remaining_configs.push_back(remaining_configs_new);
      dps_stack.push_back(curves);
      chosen_idxs.push_back({curr.first + 1, curr.second});
      chosen_chokepoints.push_back(-1);
      chosen_fpses.push_back(-1);
    }
  }
  return solution;
}

Result::ptr_t stems_simple(
  const std::set<int>& fps_options,
  const std::set<int>& chokepoints,
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  const layer_costs_t& layer_costs_subset_sums,
  double budget,
  int verbose) {
  Result::ptr_t solution = nullptr;
  int max_steps = std::min(possible_configurations.size(),
                      std::min(chokepoints.size(), fps_options.size()));
  int cnt_stems_total = 0;

  // Naive: try all stems.
  for (int num_steps = 1; num_steps <= max_steps; ++num_steps) {
    int cnt_stems = 0;
    int cnt_stems_in_budget = 0;
    int improved_stems = 0;
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
          std::make_shared<const std::vector<double>>(layer_costs_subset_sums));

        // Prune stems that exceed budget.
        if (F_MORE(stem.GetCost(), budget)) {
          continue;
        }
        cnt_stems_in_budget++;

        app_configs_t stem_configs = filter_configs(possible_configurations, stem);

        ResultCurve curve = get_pareto_curves(stem,
                                      budget,
                                      stem_configs,
                                      app_ids).back();
        if (curve.size() > 0) {
          auto result = curve.BestResult();
          if (solution == nullptr || *solution < *result) {
            solution = result;
            improved_stems++;

            std::cerr << "Improved: " << std::endl;
            std::cerr << "\t" << stem << std::endl;
            std::cerr << "\t" << *result << std::endl;
          }
        }
      } while (std::prev_permutation(chokepoint_sels.begin(),
                                     chokepoint_sels.end()));
    } while (std::prev_permutation(fps_sel.begin(), fps_sel.end()));
    cnt_stems_total += cnt_stems;
    std::cerr << num_steps << " " << cnt_stems << " " << cnt_stems_in_budget << ' ' << improved_stems << std::endl;
  }
  std::cerr << "Total stems: " << cnt_stems_total << std::endl;
  return solution;
}

// Enumerate through stems.
std::shared_ptr<Schedule> get_optimal_schedule(
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  layer_costs_t layer_costs,
  double budget,
  int verbose) {
  // Prune possible_configurations to only optimal ones.
  for (auto& kv : possible_configurations) {
    std::set<ScheduleUnit> app_configs(kv.second.begin(), kv.second.end());
    cost_t best_so_far = std::numeric_limits<cost_t>::infinity();
    for (auto ii = app_configs.begin(); ii != app_configs.end(); ) {
      if (F_LESS(ii->GetBranchCost(), best_so_far)) {
        best_so_far = ii->GetBranchCost();
        ++ii;
      } else {
        ii = app_configs.erase(ii);
      }
    }
    kv.second.assign(app_configs.begin(), app_configs.end());
  }

  // Initialise FPSes, chokepoints and max_steps.
  std::set<int> fps_options;
  std::set<int> chokepoints;
  for (const auto& kv : possible_configurations) {
    for (const auto& unit : kv.second) {
        fps_options.insert(unit.GetFPS());
        chokepoints.insert(unit.GetNumFrozen());
      }
  }
  layer_costs_t layer_costs_subset_sums = get_subset_sums(layer_costs);

  Result::ptr_t solution = stems_dp(
  // Result::ptr_t solution = stems_simple(
    fps_options,
    chokepoints,
    app_ids,
    possible_configurations,
    layer_costs_subset_sums,
    budget,
    verbose);

  assert(solution != nullptr);
  auto schedule_ = Schedule(layer_costs, budget, solution->GetSchedule());
  std::cerr << std::endl;
  std::cerr << "Schedule: " << schedule_ << std::endl;
  assert(solution->GetSchedule().size() == possible_configurations.size());
  std::cerr << "Stem Cost:" << schedule_.GetStemCost() << std::endl;
  std::cerr << schedule_.GetCost() << ' ' << solution->GetCost() << ' ';
  std::cerr << schedule_.GetAverageMetric() << ' ' << -(double)solution->GetBenefit().sum_ / app_ids.size() << std::endl;
  assert(F_EQL(schedule_.GetCost(), solution->GetCost()));
  assert(F_EQL(schedule_.GetAverageMetric(), -(double)solution->GetBenefit().sum_ / app_ids.size()));

  return std::make_shared<Schedule>(layer_costs, budget, solution->GetSchedule());
}


int main(int argc, char *argv[]) {
  std::string data_dir = argv[1];
  std::string setup_suffix = argv[2];
  bool debug = true;
  std::cout << setup_suffix << ", " << data_dir << "\n";
  run("stems_cpp", data_dir, setup_suffix, get_optimal_schedule, debug);
  return 0;
}
