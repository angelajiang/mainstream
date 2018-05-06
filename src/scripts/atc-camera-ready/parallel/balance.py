import subprocess
from time import sleep
import argparse
import math
import os
import re

DEBUG = True

class Sweeper(object):

    def __init__(self):
        self.exclusions = []
        self.dimensions = {}

    def __iter__(self):
        self.dimension_index = dict([(key, 0) for key in self.dimensions])
        self.dimension_index[self.dimension_index.keys()[0]] -= 1
        return self

    def exclude_combination(self, combo):
        self.exclusions.append(combo)

    def add_dimension(self, name, values):
        self.dimensions[name] = values

    def dimension_size(self, dimension_name):
        return len(self.dimensions[dimension_name])

    def next_index(self):
        for dimension, index in self.dimension_index.iteritems():
            if index < self.dimension_size(dimension) - 1:
                self.dimension_index[dimension] += 1
                return
            else:
                self.dimension_index[dimension] = 0
        raise StopIteration

    def exclusion_matches(self, exclusion, combo):
        for dimension, value in exclusion.iteritems():
            if combo[dimension] != value:
                return False
        return True 

    def is_excluded(self, combo):
        for exclusion in self.exclusions:
            if self.exclusion_matches(exclusion, combo):
                return True
        return False

    def next(self):
        self.next_index()
        combo = {}
        while not combo:
            for dimension, values in self.dimensions.iteritems():
                combo[dimension] = values[self.dimension_index[dimension]]
            if self.is_excluded(combo):
                self.next_index()
                combo = {}
        return combo


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("--setups_file", required=True)
    parser.add_argument("-c", "--cluster", required=True)
    parser.add_argument("-n", "--num_nodes", required=True, type=int)
    parser.add_argument("-d", "--data_dir", required=True)
    parser.add_argument("-e", "--experiment_id", required=True)
    parser.add_argument("-s", "--script", required=True)
    parser.add_argument("-b", "--budgets", required=True, type=int, nargs="+")
    parser.add_argument("-S", "--schedulers", default=["greedy", "stems_cpp"], nargs="+")
    parser.add_argument("-m", "--modes", default=["mainstream", "nosharing", "maxsharing"], nargs="+")
    return parser.parse_args()


def make_pointers_file(data_dir, experiment_id):
    return os.path.join(data_dir, "pointers.{}".format(experiment_id))


def make_result_file(data_dir, scheduler, mode, budget, experiment_id):
    return os.path.join(data_dir, "schedules", "{}.{}.sim.{}.{}".format(scheduler,
                                                                        mode,
                                                                        budget,
                                                                        experiment_id))

def lines_in_file(path):
    with open(path) as f:
        return sum(1 for line in f)


def shard_pointer_file(data_dir, experiment_id, num_nodes):
    pointers_file = make_pointers_file(data_dir, experiment_id)
    num_setups = lines_in_file(pointers_file)
    pnum = int(math.ceil(float(num_setups) / num_nodes))

    shared_experiment_ids = []
    with open(pointers_file) as f:
        for i, line in enumerate(f):
            if i % pnum == 0:
                new_experiment_id = "{}-{}".format(experiment_id, i)
                shared_experiment_ids.append(new_experiment_id)

                new_pointers_file = make_pointers_file(data_dir, new_experiment_id)
                out = open(new_pointers_file, "w")

            out.write(line)

    return shared_experiment_ids


def process_results(experiments, result_file):
    shard_files = [e.out_file for e in experiments]
    with open(result_file, 'w+') as outfile:
        for fname in shard_files:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
            os.remove(fname)


def collect_results(experiments, result_file):
    while True:
        if all([experiment.complete() for experiment in experiments]):
            process_results(experiments, result_file)
            break
        sleep(5)


def run_on_node(cmd, node):
    if not DEBUG:
        cmd = ["ssh", node] + cmd
    subprocess.Popen(cmd)


def run(experiments, nodes, result_file):
    for experiment, node in zip(experiments, nodes):
        run_on_node(experiment.get_run_command(), node)
    collect_results(experiments, result_file)


class Experiment(object):
    def __init__(self,
                 script=None,
                 data_dir=None,
                 setups_file=None,
                 experiment_id=None,
                 scheduler=None,
                 budget=None,
                 mode=None):

        self.script = script
        self.data_dir = data_dir
        self.setups_file = setups_file
        self.experiment_id = experiment_id
        self.scheduler = scheduler
        self.budget = budget
        self.mode = mode

    def get_run_command(self):
        return ["bash",
                self.script,
                self.data_dir,
                self.experiment_id,
                self.setups_file,
                str(self.budget),
                self.scheduler,
                self.mode]

    @property
    def pointer_file(self):
        return make_pointers_file(self.data_dir, self.experiment_id) 

    @property
    def out_file(self):
        return make_result_file(self.data_dir,
                                 self.scheduler,
                                 self.mode,
                                 self.budget,
                                 self.experiment_id)

    def complete(self):
        if os.path.isfile(self.out_file):
            is_done = lines_in_file(self.pointer_file) == lines_in_file(self.out_file) 
            return is_done
        else:
            return False


def main():
    args = get_args()

    experiment_ids = shard_pointer_file(args.data_dir, args.experiment_id, args.num_nodes)

    sweeper = Sweeper()
    sweeper.add_dimension("scheduler", args.schedulers)
    sweeper.add_dimension("budget", args.budgets)
    sweeper.add_dimension("mode", args.modes)
    combo1 = {"scheduler": "stems_cpp", "mode": "maxsharing"}
    combo2 = {"scheduler": "stems_cpp", "mode": "nosharing"}
    sweeper.exclude_combination(combo1)
    sweeper.exclude_combination(combo2)

    nodes = ["{}-{:02d}".format(args.cluster, i) for i in range(0, args.num_nodes)]
    for s in sweeper:
        experiments = []
        for experiment_id in experiment_ids:
            exp = Experiment(script=args.script,
                             data_dir=args.data_dir,
                             setups_file=args.setups_file,
                             scheduler=s["scheduler"],
                             experiment_id=experiment_id,
                             budget=s["budget"],
                             mode=s["mode"])
            experiments.append(exp)
        result_file = make_result_file(args.data_dir,
                                       s["scheduler"],
                                       s["mode"],
                                       s["budget"],
                                       args.experiment_id)
        run(experiments, nodes, result_file)

if __name__ == "__main__":
    main()
