import sys
sys.path.append('src/scheduler')
import scheduler_util
import Schedule
import Scheduler
from itertools import combinations, combinations_with_replacement, product, chain
import itertools
import operator
import pprint as pp
import zmq
import math
from collections import OrderedDict
from collections import Counter
import gc
import numpy as np


class DistributedScheduler:
    ### Object that performs optimization of parameters
    ### and feedback with Streamer

    def __init__(self, min_metric, apps, video_desc, model_desc, budget=350, mode="mainstream", dp=None, agg='avg', distributed_nodes=1, verbose=0, scheduler='greedy'):
        self.min_metric = min_metric
        self.apps = apps
        self.video_desc = video_desc
        self.model_desc = model_desc
        self.budget = budget
        self.mode = mode
        self.dp = dp
        self.agg = agg
        self.distributed_nodes = distributed_nodes
        self.verbose = verbose
        self.scheduler = scheduler

    def app_permutations(self, apps, distributed_nodes):
        partitions = []
        n = len(self.apps)

        all_partitions = list(product(range(distributed_nodes), repeat=n))
        for partition in all_partitions:
            assignments = []
            for node in range(distributed_nodes):
                assigned_to_node = frozenset([i for i,elem in enumerate(list(partition)) if elem == node])
                assignments.append(assigned_to_node)

            partitions.append(assignments)
        return partitions

    def generate_schedulers(self):
        app_indices = list(range(len(self.apps)))
        app_powerset = list(chain.from_iterable(combinations(app_indices, r) for r in range(len(app_indices)+1)))
        self.schedulers = dict()

        for part in app_powerset:
            part_set = frozenset(part)
            if len(part_set) == 0:
                stats = {
                    "metric": 0,
                    "rel_accs": [],
                    "fnr": 0,
                    "fpr": 0,
                    "f1": 0,
                    "cost": 0,
                    "fps": [],
                    "frozen": [],
                    "avg_rel_acc": 0,
                }
                self.schedulers[part_set] = (None, stats, [])
                continue

            part_apps_list = [self.apps[i] for i in part_set]
            s = Scheduler.Scheduler(self.min_metric, part_apps_list, self.video_desc, self.model_desc, 0)
            stats = {
                "metric": s.optimize_parameters(self.budget, mode=self.mode, dp=self.dp),
                "rel_accs": s.get_relative_accuracies(),
            }

            sched = s.make_streamer_schedule()
            stats["fnr"], stats["fpr"], stats["f1"], stats["cost"] = s.get_observed_performance(sched, s.target_fps_list)
            stats["fps"] = s.target_fps_list
            stats["frozen"] = s.num_frozen_list
            stats["avg_rel_acc"] = np.average(stats["rel_accs"])

            self.schedulers[part_set] = (s,stats, list(part_set))

    def find_best_schedule(self):
        partitions = self.app_permutations(self.apps, self.distributed_nodes)

        best_partition = None
        best_metric = -1
        for partition in partitions:
            if self.agg == 'min':
                met = -1
                for node in partition:
                    (node_s, (node_stats, node_list)) = self.schedulers[node]
                    if met == -1:
                        met = node_stats['metric']
                    else:
                        met = min(met, node_stats['metric'])
            else:
                met = 0
                for node in partition:
                    node_tup = self.schedulers[node]
                    node_s = node_tup[0]
                    node_stats = node_tup[1]
                    node_list = node_tup[2]
                    met = met + node_stats['metric'] * float(len(node)) / float(len(self.apps))

            if met > best_metric or best_metric == -1:
                best_metric = met
                best_partition = partition

        stats = {
            'metric': best_metric,
            'fnr': 0,
            'fpr': 0,
            'f1': 0,
            'cost': 0,
            'fps': [0]*len(self.apps),
            'frozen': [0]*len(self.apps),
            'rel_accs': [0]*len(self.apps),
        }
        
        print("Partition: {")
        for node in best_partition:
            node_tup = self.schedulers[node]
            node_s = node_tup[0]
            node_stats = node_tup[1]
            node_list = node_tup[2]
            print(node_list)
            stats['fnr'] = stats['fnr'] + node_stats['fnr'] * float(len(node)) / float(len(self.apps))
            stats['fpr'] = stats['fpr'] + node_stats['fpr'] * float(len(node)) / float(len(self.apps))
            stats['f1'] = stats['f1'] + node_stats['f1'] * float(len(node)) / float(len(self.apps))
            stats['cost'] = stats['cost'] + node_stats['cost'] * float(len(node)) / float(len(self.apps))

            node_index = 0
            for full_index in node_list:
                stats['fps'][full_index] = node_stats['fps'][node_index]
                stats['frozen'][full_index] = node_stats['frozen'][node_index]
                stats['rel_accs'][full_index] = node_stats['rel_accs'][node_index]
                node_index = node_index + 1

            stats['avg_rel_acc'] = np.average(stats['rel_accs'])
        print("}")
        return (stats, best_partition)

     
