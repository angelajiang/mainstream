#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

class ScheduleUnit
{
  private:

    int app_id_;
    int num_frozen_;
    int fps_;
    double metric_;
    double branch_cost_;

  public:

    ScheduleUnit(int app_id, int num_frozen, int fps, double branch_cost, double metric);

    ~ScheduleUnit(){};

    int GetAppId();

    int GetNumFrozen();

    int GetFPS();

    double GetMetric();

    double GetBranchPoint();

};

#endif
