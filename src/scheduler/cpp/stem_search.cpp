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
  const int budget,
  app_configs_t all_app_configs,
  const std::vector<std::string>& app_ids) {
  std::vector<ResultCurve> dp;
  int app_idx = 0;
  for (std::string app_id : app_ids) {
    ResultCurve results;

    // App configs allowed under stem.
    // TODO: Remove since redundant (applied earlier).
    std::set<ScheduleUnit> allowed_configs;
    for (const ScheduleUnit& unit : all_app_configs[app_id]) {
      assert(stem.Allows(unit));
      allowed_configs.insert(unit);
    }

    // Prune possible_app_configs to those that are optimal.
    cost_t best_so_far = std::numeric_limits<cost_t>::infinity();
    for (auto ii = allowed_configs.begin(); ii != allowed_configs.end(); ) {
      if (F_LESS(ii->GetBranchCost(), best_so_far)) {
        best_so_far = ii->GetBranchCost();
        ++ii;
      } else {
        ii = allowed_configs.erase(ii);
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
            double extra_cost = (app_idx == app_ids.size() - 1) ? stem.GetCost() : 0;
            if (!F_MORE(partial_result->GetCost() + unit.GetBranchCost() + extra_cost, budget)) {
              results.Add(Result(unit, partial_result, extra_cost));
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

// std::pair<app_configs_t, app_configs_t> partition_configs(
//   app_configs_t possible_configs,
//   const SharedStem& stem) {
//   app_configs_t stem_app_configs, remaining;
//   for (const auto& kv : possible_configs) {
//     std::vector<ScheduleUnit> allowed_configs, remaining_local;
//     for (const ScheduleUnit& unit : kv.second) {
//       if (stem.Allows(unit)) {
//         allowed_configs.push_back(unit);
//       } else {
//         remaining_local.push_back(unit);
//       }
//     }
//     stem_app_configs[kv.first] = allowed_configs;
//     remaining[kv.first] = remaining_local;
//   }
//   return {stem_app_configs, remaining};
// }

Result::ptr_t stems_simple(
  const std::set<int>& fps_options,
  const std::set<int>& chokepoints,
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  const layer_costs_t& layer_costs_subset_sums,
  int budget,
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

        assert(chosen_chokepoints.size() == num_steps);
        assert(chosen_fpses.size() == num_steps);

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
  int budget,
  int verbose) {
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
  assert(solution->GetSchedule().size() == app_ids.size());
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
  int budget = strtod(argv[3], NULL);
  bool debug = false;
  std::cout << setup_suffix << ", " << data_dir << "\n";
  run("stems_cpp.mainstream", data_dir, setup_suffix, get_optimal_schedule, budget, debug);
  return 0;
}
