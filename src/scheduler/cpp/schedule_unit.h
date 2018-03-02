#ifndef SCHEDULE_UNIT_H
#define SCHEDULE_UNIT_H

class ScheduleUnit
{
  public:

    int app_id;
    int num_frozen;
    int fps;
    double metric;
    double branch_cost;

    ScheduleUnit(int app_id, int num_frozen, int fps, double metric, double branch_cost){
      this->app_id = app_id;
      this->num_frozen = num_frozen;
      this->fps = fps;
      this->metric = metric;
      this->branch_cost = branch_cost;
    }

};

#endif
