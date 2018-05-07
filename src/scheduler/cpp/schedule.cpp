#include "schedule.h"
#include <algorithm>
#include <numeric>
#include <set>
#include <sstream>

string Schedule::GetFPSString(void) const
{
  stringstream ss;
  /*
  bool first = true;
  for (auto & unit : schedule_) {
    if (!first)
      ss << ",";
    ss << unit.GetFPS();
    first = false;
  }
  */

  for(unsigned u=0; u<GetNumApps(); u++) {
    ss << app_settings_[u][config_[u]].GetFPS() << ", ";
  }
  
  return  ss.str();
}

string Schedule::GetNumFrozenString(void) const
{
  stringstream ss;
  /*
  bool first = true;
  for (auto & unit : schedule_) {
    if (!first)
      ss << ",";
    ss << unit.GetNumFrozen();
    first = false;
  }
  */

  for(unsigned u=0; u<GetNumApps(); u++) {
    ss << app_settings_[u][config_[u]].GetNumFrozen() << ", ";
  }
  
  return ss.str();
}

/*
string Schedule::GetPrintStatement(){
  stringstream ss;
  
  // ss << GetNumFrozenString() + "," + GetFPSString();
  for (auto & unit : schedule_)
    ss << unit << ' ';
  
  return  ss.str();
}
*/

string Schedule::GetOutputLine(void) const
{
  stringstream ss;

  double metric = GetAverageMetric();

  ss << GetNumApps() << ", "
     << GetAverageMetric() << ", "
     << GetNumFrozenString() // << ", "
     << GetFPSString() // << ", "
     << GetBudget() << ", "
     << GetCost() ;

  return ss.str();
}

ostream& operator<<(ostream& os, const Schedule& obj)
{
  //  return os << obj.GetPrintStatement();
  return os << obj.GetOutputLine();
}

