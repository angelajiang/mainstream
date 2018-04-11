
def get_accuracy_curve(filename):
    accs = {}
    acc_invs = {}
    with open(filename) as f:
        for line in f:
            vals = line.split(",")
            num_frozen = int(vals[0])
            acc = float(vals[0])
            acc_inv = float(vals[0])
            accs[num_frozen] = acc
            acc_invs[num_frozen] = acc_inv
    return (accs, acc_invs)

