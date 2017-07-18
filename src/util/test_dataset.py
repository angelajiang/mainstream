import sys
sys.path.append('src/util')
import dataset
import scipy.misc


def run(dataset_dir, output_dir):

    # Get data
    data_X, data_y, _ = dataset.dataset(dataset_dir, 299, False)
    for i, x in enumerate(data_X):
        output_file = output_dir + "/frame-" + str(i) + ".png"
        scipy.misc.imsave(output_file, x)

if __name__ == "__main__":
    dataset_dir, output_dir = sys.argv[1:]
    run(dataset_dir, output_dir)
