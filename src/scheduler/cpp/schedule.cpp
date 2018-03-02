#include "schedule.h"
#include <iostream>
#include <set>

Schedule::Schedule(){
  vector<ScheduleUnit> schedule {};
  schedule_ = schedule;
}

double Schedule::GetCost(){
  return 0.0;
}

void Schedule::AddApp(ScheduleUnit unit) {
  schedule_.push_back(unit);
  return;
}

set<int> Schedule::GetBranchPoints(){
  set<int> branchpoints = {};
  for (auto & unit : schedule_) {
    branchpoints.insert(unit.GetBranchPoint());
  }
  return branchpoints;
}

vector<ScheduleUnit> Schedule::GetAppsBranched(){
  vector<ScheduleUnit> apps = {};
  return apps;
}

vector<ScheduleUnit> Schedule::GetAppsNotBranched(){
  vector<ScheduleUnit> apps = {};
  return apps;
}

/*
def get_cost_schedule(schedule, layer_latencies, num_layers):
    ### Cost of full schedule
    ### Measure based on sum of inference/sec of each layer
    # Schedule = [ScheduleUnit...]
    branch_points = list(set([unit.num_frozen for unit in schedule]))
    branch_points.append(num_layers)
    seg_start = 0
    cost = 0
    for seg_end in branch_points:
        seg_latency = sum([layer_latencies[i] for i in range(seg_start, seg_end)]) #doublecheck

        apps_branched, apps_not_branched = get_apps_branched(schedule, seg_end)
        seg_fps = 0
        branched_fpses = [unit.target_fps for unit in apps_branched]
        not_branched_fpses = [unit.target_fps for unit in apps_not_branched]
        if len(apps_branched) > 0: #double check
            task_fps = sum(branched_fpses)
            seg_fps += task_fps
        if len(apps_not_branched) > 0: #double check
            base_fps = max(not_branched_fpses)
            seg_fps += base_fps

        cost += seg_latency * seg_fps
        seg_start = seg_end

    return cost
 */

