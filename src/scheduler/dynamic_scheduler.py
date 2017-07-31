import sys
sys.path.append('src/scheduler')
import scheduler

def schedule(apps, num_frozen_list, model_desc):
    return scheduler.schedule(apps, num_frozen_list, model_desc)
