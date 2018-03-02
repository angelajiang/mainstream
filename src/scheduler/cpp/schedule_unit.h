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

    ScheduleUnit(int app_id, int num_frozen, int fps, double metric, double branch_cost);

    ~ScheduleUnit(){};

    int GetAppId();

    int GetNumFrozen();

    int GetFPS();

    double GetMetric();

    double GetBranchPoint();

};

#endif
