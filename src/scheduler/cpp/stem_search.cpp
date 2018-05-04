#include <cassert>
#include <fstream>
#include <functional>
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
  int budget,
  app_configs_t possible_app_configs,
  std::vector<std::string> app_ids) {
  std::vector<ResultCurve> dp;
  // cerr << stem << endl;
  // int cnt = 0;
  for (std::string& app_id : app_ids) {
    ResultCurve results;

    // App configs allowed under stem.
    std::set<ScheduleUnit> allowed_configs;
    // std::cerr << "Allowed: ";
    for (const ScheduleUnit& unit : possible_app_configs[app_id]) {
      if (stem.Allows(unit)) {
        allowed_configs.insert(unit);
        // std::cerr << unit << ",";
      }
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

    if (dp.size() == 0) {
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


std::shared_ptr<Schedule> get_optimal_schedule(
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  layer_costs_t layer_costs,
  int budget,
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
  int max_steps = std::min(app_ids.size(),
                      std::min(chokepoints.size(), fps_options.size()));

  layer_costs_t layer_costs_subset_sums = get_subset_sums(layer_costs);

  Result::ptr_t solution = nullptr;

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

        ResultCurve curve = get_pareto_curve(stem,
                                      budget,
                                      possible_configurations,
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

  assert(solution != nullptr);
  assert(solution->GetSchedule().size() == app_ids.size());
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
  // Determine what setups in the pointer file to schedule
  int pointer_start = 0;
  int pointer_num = std::numeric_limits<int>::max();

  int i = 1;
  while((i < argc) && (*argv[i] == '-') && (*(argv[i]+1) == '-')) {
    if(std::string(argv[i]) == "--pstart") {
      pointer_start = strtoul(argv[++i], NULL, 0);
      assert(pointer_start >= 0);

    }
    else if(std::string(argv[i]) == "--pnum") {
      pointer_num = strtoul(argv[++i], NULL, 0);
      assert(pointer_num >= 0);
    }
    ++i;
  }

  std::string data_dir = argv[i];
  std::string setup_suffix = argv[++i];
  int budget = strtod(argv[++i], NULL);

  bool debug = false;

  std::cout << setup_suffix << ", " << data_dir << "\n";
  run("stems_cpp.mainstream", data_dir, setup_suffix, get_optimal_schedule, budget, pointer_start, pointer_num, debug);
  return 0;
}
