from subprocess import call
import argparse
import math
import os
import re

SCHEDULERS = ["greedy", "stems_cpp"]


def get_args(simulator=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("--setups_file", required=True)
    parser.add_argument("-n", "--num_nodes", required=True, type=int)
    parser.add_argument("-d", "--data_dir", required=True)
    parser.add_argument("-e", "--experiment_id", required=True)
    parser.add_argument("-b", "--budgets", required=True, type=int, nargs="+")
    parser.add_argument("-s", "--script", required=True)
    parser.add_argument("-S", "--schedulers", default=" ".join(SCHEDULERS), nargs="+")
    return parser.parse_args()

def make_pointers_file(data_dir, experiment_id):
    return os.path.join(data_dir, "pointers.{}".format(experiment_id))

def shard_pointer_file(data_dir, experiment_id, num_nodes):
    pointers_file = make_pointers_file(data_dir, experiment_id)
    with open(pointers_file) as f:
        num_setups = sum(1 for line in f)

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


def run_file_on_node(experiment, node):
    run_remote(experiment.get_run_bash(), node)


node = 0
def get_next_node():
    name = "nodename-{}".format(node)
    node += 1
    return name


def process_results(experiments):
    pass

def collect_results(experiments, scheduler, budget):
    while True:
        if all([experiment.complete(scheduler, budget)
                for experiment in experiments]):
            process_results(experiments)
            break
        sleep(sleep_time)


def run_on_node(cmd, node):
    cmd = ["bash"] + cmd
    call(cmd)


def run(experiments, schedulers, budgets, nodes):
    for scheduler in schedulers:
        for budget in budgets:
            for experiment, node in zip(experiments, nodes):
               run_on_node(experiment.get_run_command(scheduler, budget), node)
            collect_results(experiments, scheduler, budget)


class Experiment(object):
    def __init__(self,
                 script=None,
                 data_dir=None,
                 setups_file=None,
                 experiment_id=None):

        self.script = script
        self.data_dir = data_dir
        self.setups_file = setups_file
        self.experiment_id = experiment_id

    def get_run_command(self, scheduler, budget):
        return [self.script,
                self.data_dir,
                self.experiment_id,
                self.setups_file,
                str(budget),
                scheduler]

    def complete(self, scheduler, budget):
        return True
 

def main():
    args = get_args()

    experiment_ids = shard_pointer_file(args.data_dir, args.experiment_id, args.num_nodes)
    experiments =[Experiment(
            script=args.script,
            data_dir=args.data_dir,
            experiment_id=experiment_id,
            setups_file=args.setups_file)
         for experiment_id in experiment_ids]
    nodes = ["NODE1", "NODE2"]
    run(experiments, args.schedulers, args.budgets, nodes)

    # TODO: Remove traces of pstart/pnum in future scripts

if __name__ == "__main__":
    main()
