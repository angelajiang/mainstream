#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

#include <iostream>
#include <string>

class ScheduleUnit {
  private:
    std::string app_id_;
    int num_frozen_;
    int fps_;
    double metric_;
    double branch_cost_;

  public:
    ScheduleUnit(
        std::string app_id,
        int num_frozen,
        int fps,
        double branch_cost,
        double metric);

    ~ScheduleUnit() {}

    std::string GetAppId() const;

    int GetNumFrozen() const;

    int GetFPS() const;

    double GetMetric() const;

    double GetBranchCost() const;

    std::string GetString() const;

    bool operator<(const ScheduleUnit& rhs) const;
};

std::ostream& operator<<(std::ostream& os, const ScheduleUnit& obj);

#endif
