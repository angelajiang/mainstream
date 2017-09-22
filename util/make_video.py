import pprint as pp import random
import scipy.io
import shutil
import os
import uuid


# Sunflowers are label 54. Image 5398 is classified incorrectly.
# ffmpeg -framerate 1 -i "%d.jpg" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"
#   ~/src/data/videos/sunflowers-dependent-1fps.mp4

def get_label(label_number, imagelabels_file, images_dir):
    mat = scipy.io.loadmat(imagelabels_file)
    labels = set(mat["labels"][0])
    possibilities = [l for l in labels if list(mat["labels"][0]).count(l) == label_number]
    return possibilities

def get_positive_ids(imagelabels_file, target_label):
    mat = scipy.io.loadmat(imagelabels_file)
    labels = set(mat["labels"][0])
    ids = [i for i, l in enumerate(mat["labels"][0]) \
            if l == target_label and i != 5398]
    random.shuffle(ids)
    return ids

def get_negative_ids(imagelabels_file, target_label):
    mat = scipy.io.loadmat(imagelabels_file)
    labels = set(mat["labels"][0])
    ids = [i for i, l in enumerate(mat["labels"][0]) \
            if l != target_label]
    random.shuffle(ids)
    return ids

def id_to_filename(i):
    if i < 10:
        zeroes = "0000"
    if i < 100:
        zeroes = "000"
    elif i < 1000:
        zeroes = "00"
    elif i < 10000:
        zeroes = "0"
    filename = "image_" + zeroes + str(i) + ".jpg"
    return filename

def make_video(positives, negatives, event_length_frames, non_event_length_frames,
               warmup_frames, images_dir, dst_dir, metafile_dir):

    video_id = str(uuid.uuid1())[:8]
    metafile = os.path.join(metafile_dir, video_id)
    with open(metafile, "w+") as f:

        frame_id = 0
        event_id = 0
        ordered_ids = []
        cur_positive_index = 0
        cur_negative_index = 0

        # Add frames to ignore for warmup time
        for i in range(warmup_frames):
            ordered_ids.append(positives[cur_positive_index])
            frame_id += 1
            line = str(frame_id) + ",-1,0,1\n"
            f.write(line)

        # Add positives and negatives
        while cur_positive_index < len(positives) \
                and cur_negative_index < len(negatives):
            for i in range(event_length_frames):
                ordered_ids.append(positives[cur_positive_index])
                frame_id += 1
                line = str(frame_id) + "," + str(event_id) + ",0,0\n"
                f.write(line)
            for i in range(non_event_length_frames):
                ordered_ids.append(negatives[cur_negative_index])
                frame_id += 1
                line = str(frame_id) + ",-1,1,0\n"
                f.write(line)
            cur_positive_index += 1
            cur_negative_index += 1
            event_id += 1

    # Copy frames to video directory
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    dst_full_dir = os.path.join(dst_dir, video_id)
    if not os.path.exists(dst_full_dir):
        os.makedirs(dst_full_dir)

    for i, cur_id in enumerate(ordered_ids):

        orig_file = id_to_filename(cur_id)
        orig_full_file = os.path.join(images_dir, orig_file)
        dst_full_file = os.path.join(dst_full_dir, orig_file)

        new_file_name = str(i) + ".jpg"
        new_dst_full_file = os.path.join(dst_full_dir, new_file_name)

        shutil.copyfile(orig_full_file, dst_full_file)
        os.rename(dst_full_file, new_dst_full_file)

if __name__ == "__main__":

    imagelabels_file = '/Users/angela/Downloads/imagelabels.mat'
    images_dir = '/Users/angela/src/data/image-data/oxford-flowers/images/'
    dst_dir = '/Users/angela/src/data/image-data/flowers_video'
    metafile_dir= '/Users/angela/src/private/mainstream-analysis/output/video/'

    label_id_possibilities = get_label(171, imagelabels_file, images_dir)

    label_id = 74
    positives = get_positive_ids(imagelabels_file, label_id)
    negatives = get_negative_ids(imagelabels_file, label_id)
    make_video(positives, negatives, 7, 0, 5000, images_dir, dst_dir, metafile_dir)

