#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

#include <iostream>
using namespace std;

typedef unsigned int AppId; // each app will have a unique id

class ScheduleUnit
{
  private:

    AppId app_id_;
    int num_frozen_;
    int fps_;
    double metric_;
    double branch_cost_;

  public:

    ScheduleUnit(AppId app_id, int num_frozen, int fps, double branch_cost,
		 double metric)
      : app_id_(app_id), num_frozen_(num_frozen), fps_(fps), metric_(metric),
      branch_cost_(branch_cost)
    {}

    ~ScheduleUnit(void) {};

    AppId GetAppId(void) const {return app_id_;}

    int GetNumFrozen(void) const {return num_frozen_;}

    int GetFPS(void) const {return fps_;}

    double GetMetric(void) const {return metric_;}

    double GetBranchCost(void) const {return branch_cost_;}

};

ostream& operator<<(ostream& os, const ScheduleUnit& unit);

#endif
