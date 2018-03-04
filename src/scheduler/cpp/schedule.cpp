#include "schedule.h"
#include <algorithm>
#include <numeric>
#include <set>
#include <sstream>

Schedule::Schedule(vector<double> layer_costs) : layer_costs_(layer_costs) {
  vector<ScheduleUnit> schedule {};
  schedule_ = schedule;
}

string Schedule::GetOutputLine() {
  stringstream ss;

  int num_apps = schedule_.size();
  double metric = GetAverageMetric();

  ss << num_apps << "," << 
        metric << "," << 
        GetNumFrozenString() << "," << 
        GetFPSString();

  return ss.str();
}

void Schedule::AddApp(ScheduleUnit unit) {
  schedule_.push_back(unit);
  return;
}

set<int> Schedule::GetBranchPoints(){
  set<int> branchpoints = {};
  for (auto & unit : schedule_) {
    branchpoints.insert(unit.GetNumFrozen());
  }
  branchpoints.insert(layer_costs_.size());
  return branchpoints;
}

pair<vector<int>, vector<int>> Schedule::GetAppsBranchedFPS(int branch_point){
  vector<int> apps_branched_fps = {};
  vector<int> apps_not_branched_fps = {};
  for (auto & unit : schedule_) {
    if (unit.GetNumFrozen() < branch_point) {
      apps_branched_fps.push_back(unit.GetFPS());
    } else {
      apps_not_branched_fps.push_back(unit.GetFPS());
    }
  }
  pair<vector<int>, vector<int>> pair =
    make_pair(apps_branched_fps, apps_not_branched_fps);
  return pair;
}

// TODO Add a test
double Schedule::GetCost(){

  set<int> branch_points = GetBranchPoints();
  int seg_start = 0;
  double cost = 0;
  for (auto seg_end : branch_points) {
    double seg_cost = 0;
    for (int i=seg_start; i < seg_end; i++){
      seg_cost += layer_costs_[i];
    }
    pair<vector<int>, vector<int>> apps_fps_pair = 
      GetAppsBranchedFPS(seg_end);
    vector<int> branched_fps = apps_fps_pair.first;
    vector<int> not_branched_fps = apps_fps_pair.second;

    int seg_fps = 0;
    if (branched_fps.size() > 0) {
      int task_fps = accumulate(branched_fps.begin(), branched_fps.end(), 0);
      seg_fps += task_fps;
    }
    if (not_branched_fps.size() > 0) {
      int base_fps = *(max_element(not_branched_fps.begin(), not_branched_fps.end()));
      seg_fps += base_fps;
    }
    cost += seg_cost * seg_fps;
    seg_start = seg_end;
  }

  return cost;
}

double Schedule::GetAverageMetric(){
  double average_metric = 0.0;
  for (auto & unit : schedule_) {
    average_metric += unit.GetMetric();
  }
  average_metric /= schedule_.size();
  return average_metric;
}

string Schedule::GetFPSString() {
  stringstream ss;

  bool first = true;
  for (auto & unit : schedule_) {
    if (!first)
      ss << ",";
    ss << unit.GetFPS();
    first = false;
  }
  return  ss.str();
}

string Schedule::GetNumFrozenString() {
  stringstream ss;

  bool first = true;
  for (auto & unit : schedule_) {
    if (!first)
      ss << ",";
    ss << unit.GetNumFrozen();
    first = false;
  }
  return ss.str();
}

string Schedule::GetPrintStatement(){
  stringstream ss;
  ss << GetNumFrozenString() + "," + GetFPSString();
  return  ss.str();
}

ostream& operator<<(ostream& os, Schedule& obj) {

  return os << obj.GetPrintStatement();

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

