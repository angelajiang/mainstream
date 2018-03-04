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

    string GetOutputLine();

    void AddApp(ScheduleUnit);

    double GetCost();

    set<int> GetBranchPoints();

    pair<vector<int>, vector<int>> GetAppsBranchedFPS(int);

    double GetAverageMetric();

    string GetNumFrozenString();

    string GetFPSString();

    string GetPrintStatement();

};

ostream& operator<<(ostream&, Schedule&);

#endif
