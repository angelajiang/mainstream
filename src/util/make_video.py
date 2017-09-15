import pprint as pp
import random
import scipy.io
import shutil
import os
import uuid
from keras.preprocessing.image import ImageDataGenerator


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
               warmup_frames, human_label, images_dir, dst_dir, metafile_dir, dependent=False):

    datagen = ImageDataGenerator(
        featurewise_center=False,
        samplewise_center=False,
        featurewise_std_normalization=False,
        samplewise_std_normalization=False,
        zca_whitening=False,
        rotation_range=45,
        width_shift_range=0.25,
        height_shift_range=0.25,
        horizontal_flip=True,
        vertical_flip=True,
        zoom_range=0.5,
        channel_shift_range=0.5,
        fill_mode='nearest')

    video_id = str(uuid.uuid1())[:8]
    if dependent:
        video_name = video_id + "-dependent"
    else:
        video_name = video_id + "-independent"
    video_name = video_name + "-" + human_label
    metafile = os.path.join(metafile_dir, video_name)
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
        while cur_positive_index + event_length_frames < len(positives) \
                and cur_negative_index + non_event_length_frames < len(negatives):
            for i in range(event_length_frames):
                ordered_ids.append(positives[cur_positive_index])
                frame_id += 1
                line = str(frame_id) + "," + str(event_id) + ",0,0\n"
                f.write(line)
                if dependent:
                    cur_positive_index += 1
            for i in range(non_event_length_frames):
                ordered_ids.append(negatives[cur_negative_index])
                frame_id += 1
                line = str(frame_id) + ",-1,1,0\n"
                f.write(line)
                if dependent:
                    cur_negative_index += 1
            if not dependent:
                cur_positive_index += 1
                cur_negative_index += 1
            event_id += 1

    # Copy frames to video directory
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    dst_full_dir = os.path.join(dst_dir, video_name)
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
    return video_name

if __name__ == "__main__":

    ''' #Seattle
    imagelabels_file = '/Users/angela/Downloads/imagelabels.mat'
    images_dir = '/Users/angela/src/data/image-data/oxford-flowers/images/'
    dst_dir = '/Users/angela/src/data/image-data/flowers_video'
    metafile_dir= '/Users/angela/src/private/mainstream-analysis/output/video/'
    '''

    # Orca
    imagelabels_file = '/users/ahjiang/image-data/video/oxford-flowers/imagelabels.mat'
    images_dir = '/users/ahjiang/image-data/video/oxford-flowers/images/'
    dst_dir = '/users/ahjiang/image-data/video/flowers_video'
    metafile_dir= '/users/ahjiang/src/mainstream/log/videos/flowers/'

    positives = get_positive_ids(imagelabels_file, 74)
    negatives = get_negative_ids(imagelabels_file, 74)
    human_label = "rose-event7-buffer5000"
    video_name = make_video(positives, negatives, 7, 0, 5000, human_label, images_dir, dst_dir, metafile_dir, True)
    print video_name

