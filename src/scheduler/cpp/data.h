#ifndef DATA_H
#define DATA_H

#include <string>
#include <memory>
#include <unordered_map>
#include <vector>
#include "types/schedule.h"
#include "types/schedule_unit.h"
#include "types/utility.h"

typedef std::shared_ptr<Schedule> (*scheduler_fn_ptr) (
  std::vector<std::string> app_ids,
  app_configs_t possible_configurations,
  layer_costs_t layer_costs,
  double budget,
  int verbose);

std::unordered_map<std::string, std::vector<ScheduleUnit>> parse_configurations_file(
    std::string configurations_file);

std::vector<double> parse_model_file(std::string model_file);

double parse_environment_file(std::string environment_file);

void run(const std::string& scheduler_type,
         const std::string& data_dir,
         const std::string& pointer_suffix,
         scheduler_fn_ptr scheduler_fn,
         double budget,
         bool debug);

#endif  // DATA_H
