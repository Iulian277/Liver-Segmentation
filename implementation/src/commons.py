import numpy as np
import argparse
import os
import math
import random
import sys
import time

from PIL import Image

import matplotlib as mpl
import matplotlib.pyplot as plt

# If the liver has a volume > threshold, then the liver is considered to be in the `big` case
# Otherwise, the CT scanned only a small portion of the liver which has the shape of an ellipse
LIVER_VOLUME_THRESHOLD = 15000
OUTPUT_FOLDER_PATH = '../output'


def parse_args():
    """ This function grabs and returns the arguments with which the program was runned """
    parser = argparse.ArgumentParser(description='Arguments for liver segmentation')
    parser.add_argument('hu_mat_input', type=str)
    parser.add_argument('hu_seg_input', type=str)
    return parser.parse_args()


def file_to_matrix(path):
    """ This function parses a matrix written in a file to a numpy array """
    with open(path, 'r') as f:
        mat = [[int(num) for num in line.split(' ')] for line in f]
    return np.array(mat)


def matrix_to_file(testcase_index, mat, filename):
    """ This function writes a numpy array matrix in a given file"""
    path = os.path.join(OUTPUT_FOLDER_PATH, testcase_index, filename)
    np.savetxt(path, mat, fmt='%d', delimiter=' ')


def translate_ranges(img, from_range_low, from_range_high, to_range_low, to_range_high):
    """ This function does a linear interpolation and translates the interval [a, b] into [x, y] """
    return np.interp(img,
                     (from_range_low, from_range_high),
                     (to_range_low, to_range_high))


def save_fig(testcase_index, img, img_name, fig_extension='png'):
    """ This function saves a `img` at the given `path` """
    img = translate_ranges(img, img.min(), img.max(), 0, 255).astype(np.uint8)
    path = os.path.join(OUTPUT_FOLDER_PATH, testcase_index, img_name + '.' + fig_extension)
    Image.fromarray(img).save(path)


def save_optimal_segmentation(hu_mat, snake_seg, testcase_index, fig_extension='png'):
    """ This function is used for saving the `overlay` image (plot 2 figures on the same plot) """
    plt.figure(figsize=(512 / 300, 512 / 300))
    plt.axis('off')
    plt.axes([0, 0, 1, 1])
    plt.imshow(hu_mat, cmap='gray')
    plt.plot(snake_seg[:, 1], snake_seg[:, 0], '-b', lw=0.25)
    path = os.path.join(OUTPUT_FOLDER_PATH, testcase_index, 'overlay.' + fig_extension)
    plt.savefig(path, dpi=300)
