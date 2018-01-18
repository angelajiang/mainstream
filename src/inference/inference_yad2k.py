#! /usr/bin/env python
"""Run a YOLO_v2 style detection model on test images."""
import argparse
import numpy as np
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()
import seaborn as sns
sns.set_style('whitegrid')

sys.path.append("YAD2K/util")
from inference import run_inference


parser = argparse.ArgumentParser(
    description='Run a YOLO_v2 style detection model on test images..')
parser.add_argument(
    '-m',
    '--model_path',
    help='path to h5 model file containing body'
    'of a YOLO_v2 model')
parser.add_argument(
    '-a',
    '--anchors_path',
    help='path to anchors file, defaults to yolo_anchors.txt',
    default=os.path.join('~', 'models', 'yad2k_model_data', 'yolo-coco_anchors.txt'))
parser.add_argument(
    '-c',
    '--classes_path',
    help='path to classes file, defaults to coco_classes.txt',
    default=os.path.join('~', 'models', 'yad2k_model_data', 'coco_classes.txt'))
parser.add_argument(
    '--mode',
    help='{0: dir, 1:npz}',
    default='0')
parser.add_argument(
    '-t',
    '--test_dir',
    help='path to directory of test images, defaults to images/',
    default='images')
parser.add_argument(
    '-r',
    '--result_path',
    help='path to result out path',
    default=os.path.join(''))
parser.add_argument(
    '-o',
    '--output_image_path',
    help='path to output test images, defaults to images/out',
    default='images/out')
parser.add_argument(
    '-s',
    '--score_threshold',
    type=float,
    help='threshold for bounding box scores, default 0',
    default=0)
parser.add_argument(
    '-iou',
    '--iou_threshold',
    type=float,
    help='threshold for non max suppression IOU, default .5',
    default=.5)
parser.add_argument(
    '-map',
    '--map_iou_threshold',
    type=float,
    help='threshold for mAP, default .5',
    default=.5)
parser.add_argument(
    '-p',
    '--plot_file',
    help='File to save precision vs recall plot',
    default="data/plots/pr.pdf")
parser.add_argument(
    '-id',
    '--identifier',
    help='Reference ID for logging (e.g., num frozen)',
    default="")
parser.add_argument(
    '-ci',
    '--class_index',
    type=int,
    help='Target class index to transform into 0s',
    default=0)
parser.add_argument(
    '-ns',
    '--num_saved_images',
    type=int,
    help='Number of images to save with bbs',
    default=0)


def _main(args):

    model_path = os.path.expanduser(args.model_path)
    assert model_path.endswith('.h5'), 'Keras model must be a .h5 file.'
    anchors_path = os.path.expanduser(args.anchors_path)
    classes_path = os.path.expanduser(args.classes_path)

    input_mode = int(os.path.expanduser(args.mode))
    assert input_mode == 0 or input_mode == 1, 'Input mode must be in {0,1}'
    test_path = os.path.expanduser(args.test_dir)

    output_image_path = os.path.expanduser(args.output_image_path)
    result_path = os.path.expanduser(args.result_path)

    if not os.path.exists(output_image_path):
        print('Creating output path {}'.format(output_image_path))
        os.mkdir(output_image_path)

    with open(anchors_path) as f:
        anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        anchors = np.array(anchors).reshape(-1, 2)

    mAP, f1s, precisions, recalls = run_inference(model_path,
                                            anchors,
                                            classes_path,
                                            test_path,
                                            output_image_path,
                                            input_mode,
                                            args.score_threshold,
                                            args.iou_threshold,
                                            args.map_iou_threshold,
                                            args.class_index,
                                            args.num_saved_images)

    plt.scatter(recalls, precisions)
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.savefig(args.plot_file)
    plt.clf()

    max_i = np.argmax(f1s)
    max_recall = recalls[max_i]
    max_precision = precisions[max_i]
    with open(result_path, "a+") as f:
        line = "%s,%.6g,%.6g,%.6g,%s\n" % (args.identifier,
                                           mAP,
                                           max_precision,
                                           max_recall,
                                           model_path)
        f.write(line)

if __name__ == '__main__':
    _main(parser.parse_args())
