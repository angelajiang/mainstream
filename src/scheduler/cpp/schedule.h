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
    double budget_;

  public:

    Schedule(vector<double>, double budget);

    Schedule(vector<double>, double budget, vector<ScheduleUnit> schedule);

    ~Schedule(){};

    string GetOutputLine();

    void AddApp(ScheduleUnit);

    double GetCost();

    double GetBudget();

    set<int> GetBranchPoints();

    pair<vector<int>, vector<int>> GetAppsBranchedFPS(int);

    double GetAverageMetric();

    string GetNumFrozenString();

    string GetFPSString();

    string GetPrintStatement();

};

ostream& operator<<(ostream&, Schedule&);

#endif
