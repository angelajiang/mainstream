#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

#include <iostream>
#include <string>
using namespace std;

class ScheduleUnit {
  private:
    string app_id_;
    int num_frozen_;
    int fps_;
    double metric_;
    double branch_cost_;

  public:
    ScheduleUnit(
        string app_id,
        int num_frozen,
        int fps,
        double branch_cost,
        double metric);

    ~ScheduleUnit() {}

    string GetAppId() const;

    int GetNumFrozen() const;

    int GetFPS() const;

    double GetMetric() const;

    double GetBranchCost() const;
};

#endif
