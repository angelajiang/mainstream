
import sys
sys.path.append('src/inference')
import write_p_hits


if __name__ == "__main__":
    #AFN

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


    for d in dataset_dirs:
        size = write_p_hits.get_dataset_size(d)
        print d, size

    strides = range(1, 301, 1)
    #within_frames_slo = [1, 10, 20, 30, 40, 50]

    model_path = "/users/ahjiang/models/trains-new/trains-no-afn-313"
    #acc = write_p_hits.get_accuracy(dataset_dirs, model_path)
    acc = .93972

    #cp = get_conditional_probability(dataset_dirs, model_path)
    cp = 0.1664

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-correlation"
    write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, False, cp)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-dependent-whole"
    write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, False)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-independent-whole"
    write_p_hits.runB(dataset_dirs, model_path, strides, acc, output_file, True)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-random"
    #write_p_hits.runC(dataset_dirs, model_path, strides, output_file)

    output_file = "/users/ahjiang/src/mainstream-analysis/output/mainstream/frame-rate/no-afn/train/v2/trains-313-empirical-temporal"
    #write_p_hits.runD(dataset_dirs, model_path, strides, output_file)
