import pprint as pp
import sys

def get_accuracy_curve(filename, adjustment=0.0):
    accs = {}
    acc_invs = {}
    with open(filename) as f:
        for line in f:
            vals = line.split(",")
            num_frozen = int(vals[0])
            acc = float(vals[1])
            acc_inv = float(vals[2])
            accs[num_frozen] = min(acc + adjustment, 1.0)
            acc_invs[num_frozen] = acc_inv

    # Make pareto optimal curve
    # As sharing decreases, accuracy should only increase

    max_num_frozen = max(accs.keys())
    prev_acc = accs[max_num_frozen]
    prev_acc_inv = acc_invs[max_num_frozen]

    for num_frozen in reversed(sorted(accs.keys())):
        acc = accs[num_frozen]
        acc_inv = acc_invs[num_frozen]

        if prev_acc > acc:
            accs[num_frozen] = prev_acc
            acc_invs[num_frozen] = prev_acc_inv

        prev_acc = accs[num_frozen]
        prev_acc_inv = acc_invs[num_frozen]

    return (accs, acc_invs)

