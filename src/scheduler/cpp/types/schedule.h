#ifndef SCHEDULE_H
#define SCHEDULE_H

#include <iostream>
#include <set>
#include <vector>
#include <utility>
#include "schedule_unit.h"

class Schedule
{
  private:

    std::vector<ScheduleUnit> schedule_;
    std::vector<double> layer_costs_;
    double budget_;

  public:

    Schedule(std::vector<double>, double budget);

    Schedule(std::vector<double>, double budget, std::vector<ScheduleUnit> schedule);

    ~Schedule(){};

    std::string GetOutputLine();

    void AddApp(ScheduleUnit);

    double GetCost();

    double GetStemCost();

    double GetBudget();

    std::set<int> GetBranchPoints();

    std::pair<std::vector<int>, std::vector<int>> GetAppsBranchedFPS(int);

    double GetAverageMetric();

    std::string GetNumFrozenString();

    std::string GetFPSString();

    std::string GetPrintStatement();

};

std::ostream& operator<<(std::ostream&, Schedule&);

#endif
