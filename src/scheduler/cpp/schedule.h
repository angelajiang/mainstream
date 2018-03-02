#ifndef SCHEDULE_H
#define SCHEDULE_H


#include<set>
#include<vector>
#include "schedule_unit.h"

using namespace std;

class Schedule
{
  private: 

    vector<ScheduleUnit> schedule_;

  public:

    Schedule();

    ~Schedule(){};

    void AddApp(ScheduleUnit);

    double GetCost();

    set<int> GetBranchPoints();

    vector<ScheduleUnit> GetAppsBranched();

    vector<ScheduleUnit> GetAppsNotBranched();

};

#endif
