
import sys
sys.path.append('src/inference')
import write_p_hits


if __name__ == "__main__":
    # Train AFN

    dataset_dirs = [
                    "/users/ahjiang/image-data/instances/train_images_resized/a/",
                    "/users/ahjiang/image-data/instances/train_images_resized/f/",
                    "/users/ahjiang/image-data/instances/train_images_resized/n/",
                    "/users/ahjiang/image-data/instances/train_images_resized/1/",
                    "/users/ahjiang/image-data/instances/train_images_resized/2/",
                    "/users/ahjiang/image-data/instances/train_images_resized/3/",
                    "/users/ahjiang/image-data/instances/train_images_resized/4/",
                    "/users/ahjiang/image-data/instances/train_images_resized/5/"
                    ]

    # Train easy

    dataset_dirs = [
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/1/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/2/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/3/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/5/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/38/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/42/",
            "/datasets/BigLearning/ahjiang/image-data/instances/train_images_instances_resized_easy/43/"
            ]

    model_paths = [
                    "/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-0",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-15",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-21",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-27",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-33",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-39",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-45",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-51",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-57",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-63",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-69",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-81",
                    "/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-84"]

    #with open("out-train-0", "w+") as f:
    #    for model_path in model_paths:
    #        acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 0)
    #        cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 0)
    #        line = model_path + "," + str(acc) + "," + str(cp) + "\n"
    #        f.write(line)

    #with open("out-train-1", "w+") as f:
    #    for model_path in model_paths:
    #        acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 1)
    #        cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 1)
    #        line = model_path + "," + str(acc) + "," + str(cp) + "\n"
    #        f.write(line)

    # Train FP

    dataset_dirs = [
            "/datasets/BigLearning/ahjiang/image-data/test/train_easy/no-train/"
            ]

    model_paths = [
                    "/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-0",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-15",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-21",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-27",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-33",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-39",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-45",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-51",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-57",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-63",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-69",
                    #"/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-81",
                    "/users/ahjiang/models/atc/trains/mobilenets/train-easy-40-0.0001-84"]

    #with open("out-train-fp-0", "w+") as f:
    #    for model_path in model_paths:
    #        acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 0)
    #        cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 0)
    #        line = model_path + "," + str(acc) + "," + str(cp) + "\n"
    #        f.write(line)

    #with open("out-train-fp-1", "w+") as f:
    #    for model_path in model_paths:
    #        acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 1)
    #        cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 1)
    #        line = model_path + "," + str(acc) + "," + str(cp) + "\n"
    #        f.write(line)

    # Pedestrian easy

    dataset_dirs = [
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/34/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/35/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/36/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/37/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/38/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/4/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/40/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/41/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/42/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/43/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/44/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/45/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/46/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/47/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/48/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/49/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/5/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/50/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/51/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/6/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/7/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/8/",
            "/datasets/BigLearning/ahjiang/image-data/instances/atrium/pedestrian/9/"
            ]

    model_paths = [
                    "/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-0",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-15",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-21",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-27",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-33",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-39",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-45",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-51",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-57",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-63",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-69",
                    #"/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-81",
                    "/users/ahjiang/models/atc/pedestrian/atrium/atrium-mobilenets-84"
                  ]

    with open("out-pedestrian-0", "w+") as f:
        for model_path in model_paths:
            acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 0)
            cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 0)
            line = model_path + "," + str(acc) + "," + str(cp) + "\n"
            f.write(line)

    with open("out-pedestrian-1", "w+") as f:
        for model_path in model_paths:
            acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 1)
            cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 1)
            line = model_path + "," + str(acc) + "," + str(cp) + "\n"
            f.write(line)

    ## Pedestrain FP

    dataset_dirs = [
            "/datasets/BigLearning/ahjiang/image-data/test/pedestrian/no-pedestrian"
            ]

    with open("out-pedestrian-fp-0", "w+") as f:
        for model_path in model_paths:
            acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 0)
            cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 0)
            line = model_path + "," + str(acc) + "," + str(cp) + "\n"
            f.write(line)

    with open("out-pedestrian-fp-1", "w+") as f:
        for model_path in model_paths:
            acc = write_p_hits.get_accuracy(dataset_dirs, model_path, 1)
            cp = write_p_hits.get_conditional_probability(dataset_dirs, model_path, 1)
            line = model_path + "," + str(acc) + "," + str(cp) + "\n"
            f.write(line)

    for d in dataset_dirs:
        size = write_p_hits.get_dataset_size(d)
        print d, size

    strides = range(1, 301, 1)
    #within_frames_slo = [1, 10, 20, 30, 40, 50]

    #acc = .93972 # Train AFN
    #cp = 0.1664  # Train easy

    #output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-correlation"
    #write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, False, cp)

    #output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-dependent-whole"
    #write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, False)

    #output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-independent-whole"
    #write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, True)

    #output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-random"
    ##write_p_hits.runC(dataset_dirs, model_path, strides, output_file)

    #output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-temporal"
    ##write_p_hits.runD(dataset_dirs, model_path, strides, output_file)
