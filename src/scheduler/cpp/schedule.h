#ifndef SCHEDULE_H
#define SCHEDULE_H


#include <iostream>
#include<set>
#include<vector>
#include "schedule_unit.h"

using namespace std;

class Schedule
{
  private: 

    vector<ScheduleUnit> schedule_;
    vector<double> layer_costs_;

  public:

    Schedule(vector<double>);

    ~Schedule(){};

    void AddApp(ScheduleUnit);

    double GetCost();

    set<int> GetBranchPoints();

    pair<vector<int>, vector<int>> GetAppsBranchedFPS(int);

    double GetAverageMetric();

    string GetPrintStatement();

};

ostream& operator<<(ostream&, Schedule&);

#endif
