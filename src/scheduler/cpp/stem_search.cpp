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
#include "types/combinator.h"

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

    // Try all combinations of FPSes and chokepoints.
    Combinator comb(fps_options, chokepoints, num_steps);

    do {
      const auto& chosen_fpses = comb.FPSes();
      const auto& chosen_chokepoints = comb.Chokepoints();
      cnt_stems++;
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
    } while (comb.Next() != -1);
    cnt_stems_total += cnt_stems;
    std::cerr << num_steps << " " << cnt_stems << " " << cnt_stems_in_budget << ' ' << improved_stems << std::endl;
  }
  std::cerr << "Total stems: " << cnt_stems_total << std::endl;
  return solution;
}


Result::ptr_t stems_parallel(
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

    // Try all combinations of FPSes and chokepoints.
    Combinator comb(fps_options, chokepoints, num_steps);

    std::vector<SharedStem> stems;
    do {
      const auto& chosen_fpses = comb.FPSes();
      const auto& chosen_chokepoints = comb.Chokepoints();
      cnt_stems++;
      SharedStem stem(chosen_chokepoints, chosen_fpses,
        std::make_shared<const std::vector<double>>(layer_costs_subset_sums));

      // Prune stems that exceed budget.
      if (F_MORE(stem.GetCost(), budget)) {
        continue;
      }
      cnt_stems_in_budget++;
      stems.push_back(stem);
    } while (comb.Next() != -1);

    // Result sol_copy = *solution;
    #pragma omp parallel
    {
      Result::ptr_t local_sol = nullptr;
      // std::make_shared<Result>(sol_copy);
      #pragma omp for
      for (int i = 0; i < stems.size(); i++) {
        const auto& stem = stems[i];
        app_configs_t stem_configs = filter_configs(possible_configurations, stem);

        ResultCurve curve = get_pareto_curves(stem,
                                      budget,
                                      stem_configs,
                                      app_ids).back();
        if (curve.size() > 0) {
          auto result = curve.BestResult();
          if (local_sol == nullptr || *local_sol < *result) {
            local_sol = result;
            // improved_stems++;

            // std::cerr << "Improved: " << std::endl;
            // std::cerr << "\t" << stem << std::endl;
            // std::cerr << "\t" << *result << std::endl;
          }
        }
      }

      #pragma omp critical
      {
        if (solution == nullptr || *solution < *local_sol) {
          solution = local_sol;
        }
      }
    }
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

  Result::ptr_t solution = stems_parallel(
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
