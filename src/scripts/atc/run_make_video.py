
import sys
sys.path.append('src/util')
import make_video

# Sunflowers are label 54. Image 5398 is classified incorrectly.
# ffmpeg -framerate 1 -i "%d.jpg" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"
#   ~/src/data/videos/sunflowers-dependent-1fps.mp4

if __name__ == "__main__":

    # Orca
    # base = '/usr0/home/dlwong/Projects'
    base = '/users/ahjiang'
    # base2 = '/usr0/home/dlwong/Dropbox/CMU/Projects/mainstream'
    base2 = '/users/ahjiang/src/'
    imagelabels_file = base + '/image-data/video/oxford-flowers/imagelabels.mat'
    images_dir = base + '/image-data/video/oxford-flowers/images/'
    dst_dir = base + '/image-data/video/flowers_video'
    metafile_dir = base2 + '/mainstream/log/videos/flowers/'

    label_numbers = {"daisy": 49}

    '''
    possibilities = get_label(49, imagelabels_file, images_dir)
    for p in possibilities:
        positives = get_positive_ids(imagelabels_file, p)
        print p, positives[0]
        '''

    positives = get_positive_ids(imagelabels_file, label_numbers["daisy"])
    negatives = get_negative_ids(imagelabels_file, label_numbers["daisy"])
    human_label = "daisy-p3-n7-buffer2500"
    human_label = "test"
    video_name = make_video.make_video(positives, negatives, 1, 1, 10,
                                       human_label, images_dir, dst_dir,
                                       metafile_dir, False)
    perturbed_video_name = make_perturbed_video(dst_dir, video_name)
    print video_name, perturbed_video_name
