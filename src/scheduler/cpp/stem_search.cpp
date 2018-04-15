#include <algorithm>
#include <cassert>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <set>
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

ResultCurve get_pareto_curve(
  const SharedStem& stem,
  const double budget,
  app_configs_t possible_app_configs,
  const std::vector<std::string>& app_ids,
  std::vector<ResultCurve> dp = {}) {
  // cerr << stem << endl;
  // int cnt = 0;
  int app_idx = 0;
  for (std::string app_id : app_ids) {
    ResultCurve results;

    // App configs allowed under stem.
    std::set<ScheduleUnit> allowed_configs;
    // std::cerr << "Allowed: ";
    for (const ScheduleUnit& unit : possible_app_configs[app_id]) {
      assert(stem.Allows(unit));
      // if (stem.Allows(unit)) {
      //   allowed_configs.insert(unit);
      //   // std::cerr << unit << ",";
      // }
    }

    // Prune possible_app_configs to those that are optimal.
    // TODO: Remove since redundant (applied earlier?)
    cost_t best_so_far = std::numeric_limits<cost_t>::infinity();
    for (auto ii = allowed_configs.begin(); ii != allowed_configs.end(); ) {
      if (F_LESS(ii->GetBranchCost(), best_so_far)) {
        best_so_far = ii->GetBranchCost();
        ++ii;
      } else {
        ii = allowed_configs.erase(ii);
      }
    }

    if (app_idx == 0) {
      for (auto ii = allowed_configs.rbegin(); ii != allowed_configs.rend(); ++ii) {
        const ScheduleUnit& app_config_unit = *ii;
        // results.Add(std::make_shared<Result>(app_config_unit, stem.GetCost()));
        results.Add(Result(app_config_unit, stem.GetCost()));
      }
    } else {
      for (const auto& partial_result : dp[dp.size() - 1]) {
        for (auto ii = allowed_configs.rbegin(); ii != allowed_configs.rend(); ++ii) {
          const ScheduleUnit& unit = *ii;
          // Prune configurations that are over budget.
          if (!F_MORE(partial_result->GetCost() + unit.GetBranchCost(), budget)) {
            // results.Add(std::make_shared<Result>(unit, partial_result));
            results.Add(Result(unit, partial_result));
          } else {
            // Since we are enumerating allowed_configs in increasing F1/weight,
            // we can break.
            break;
          }
        }
      }
      app_idx++;
    }
    // cerr << "\t" << ++cnt << " " << results.size() << endl;
    results.Finalize();
    dp.push_back(results);
  }
  if (dp[dp.size() - 1].size() > 0) {
    dp[dp.size() - 1].BestResult();
  }
  return dp[dp.size() - 1];
}

app_configs_t filter_configs(app_configs_t possible_configs, const SharedStem& stem) {
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

  // TODO:
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

  std::vector<int> chosen_fpses, chosen_chokepoints;
  chosen_fpses.reserve(max_steps);
  chosen_chokepoints.reserve(max_steps);

  // Enter a config (add one step, get incremented to it)
  // - run and add its dp values to the stack
  // Exit a config (get incremented away, reach end & back one step)
  // - remove its dp values off the stack

  // At each node
  // - run by itself (use -1 as the end string)
  // - if possible, go one deeper
  // 1$
  // 12$
  // 123$
  // 124$
  // 13$
  // 134$
  // 14$

  // Add one step
  // -
  //
  // Same steps, but increment the chosen one
  // Reduce one step
  //

  while (next_stem) {
    SharedStem stem(chosen_chokepoints, chosen_fpses,
      std::make_shared<const std::vector<double>>(layer_costs_subset_sums));
    if (F_MORE(stem.GetCost(), budget)) {
      continue;
    }


    app_configs_t stem_configs_delta = filter_configs(prev_stem_configs, stem);
    // gotta add these back later

    ResultCurve curve = get_pareto_curve(stem, budget, stem_configs, app_ids);

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

        app_configs_t stem_configs = filter_configs(possible_app_configs, stem);

        ResultCurve curve = get_pareto_curve(stem,
                                      budget,
                                      stem_configs,
                                      app_ids);
        if (curve.size() > 0) {
          auto result = curve.BestResult();
          if (solution == nullptr || *solution < *result) {
            solution = result;
            improved_stems++;

            // std::cerr << "Improved: " << std::endl;
            // std::cerr << "\t" << stem << std::endl;
            // std::cerr << "\t" << *result << std::endl;
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

  Result::ptr_t solution = stems_simple(
    fps_options,
    chokepoints,
    app_ids,
    possible_configurations,
    layer_costs_subset_sums,
    budget,
    verbose);

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
