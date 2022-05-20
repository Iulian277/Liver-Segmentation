from commons import *

import os
import re

from pipeline import Pipeline
from transformation import Transformation
from operations import *

# General usage images
hu_mat = None
hu_seg = None
hu_mat_path = None
hu_seg_path = None


def base_pipeline():
    """ This function creates the `base pipeline` used for liver segmentation """

    pipeline = Pipeline('base_pipeline')

    pipeline.add(Transformation('HU-thresh',    lambda img: slice_window(img, level=150, window=50)))
    pipeline.add(Transformation('Norm',         lambda img: normalize(img, img.min(), img.max())))
    pipeline.add(Transformation('ROI-1',        lambda img: roi(img, hu_seg)))
    pipeline.add(Transformation('Bin',          lambda img: binarize(img)))
    pipeline.add(Transformation('Rem-small-1',  lambda img: remove_small_objects(img)))
    pipeline.add(Transformation('Morph-dil',    lambda img: morphology_dilation(img)))
    pipeline.add(Transformation('ROI-2',        lambda img: roi(img, hu_seg, True, 15)))
    pipeline.add(Transformation('Diam-open',    lambda img: diameter_opening(img)))
    pipeline.add(Transformation('Area-close',   lambda img: morphology_area_closing(img)))
    pipeline.add(Transformation('Area-open',    lambda img: morphology_area_opening(img)))
    pipeline.add(Transformation('Rem-small-2',  lambda img: remove_small_pixels(img, 10)))
    pipeline.add(Transformation('Sobel',        lambda img: sobel(img)))
    pipeline.add(Transformation('Rem-small-3',  lambda img: remove_small_pixels(img, 20)))
    pipeline.add(Transformation('Dilation-1',   lambda img: morphology_dilation(img)))
    pipeline.add(Transformation('Dilation-2',   lambda img: morphology_dilation(img)))
    pipeline.add(Transformation('Dilation-3',   lambda img: morphology_dilation(img)))
    pipeline.add(Transformation('Fill-holes',   lambda img: fill_holes(img)))
    pipeline.add(Transformation('Snake',        lambda img: active_contour(img, hu_seg)))

    return pipeline


def run_segementation(pipeline):
    """
    This function runs the segmentation process and generates 3 files (mask-img, mask-matrix, overlay-img)
    The files are located in the `implementation/output/testcase_index/` directory

    You can add your own input tests in a `implementation/input/testcase_index/` directory
    The program will create a new output file corresponding to the given `testcase_index`
    """

    start = time.time()
    liver_mask = pipeline.transform(hu_mat)
    end = time.time()
    print('-' * 55)
    print('Elapsed time: [{:.2f} sec]'.format(end - start))

    testcase_numbers = []
    reg_expr = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    if re.search(reg_expr, hu_mat_path) is not None:
        for catch in re.finditer(reg_expr, hu_mat_path):
            testcase_numbers.append(catch[0])

    testcase_index = 'curr_test'
    if len(testcase_numbers) != 0:
        testcase_index = testcase_numbers[0]

    if not os.path.isdir(os.path.join(OUTPUT_FOLDER_PATH, testcase_index)):
        os.mkdir(os.path.join(OUTPUT_FOLDER_PATH, testcase_index))
    save_fig(testcase_index, liver_mask, 'mask')
    matrix_to_file(testcase_index, liver_mask, 'optim.out')
    save_optimal_segmentation(hu_mat, measure.find_contours(liver_mask, 0.95)[0], testcase_index)

def big_liver():
    """
    This function runs the segmentation if the CT
    also scanned a lot of small regions around the liver
    """

    pipeline = base_pipeline()
    run_segementation(pipeline)


def small_liver():
    """
    This function runs the segmentation if the CT scanned
    only a small portion of the liver which has the shape of an ellipse.

    There are only 2 changes from the `big_liver` segmentation.
    Here the liver is highlighted and the very small regions around it are removed,
    while in the big liver case the regions around the liver are highlighted
    (this approach leads to good results for both types of segmentation)
    """

    pipeline = base_pipeline()
    pipeline.replace('HU-thresh',
      Transformation('HU-thresh',   lambda img: slice_window(img, level=100, window=50)))
    pipeline.replace('Rem-small-1',
      Transformation('Rem-small-1', lambda img: remove_small_objects(img, min_size=1000, ret_mask=True)))
    run_segementation(pipeline)


if __name__ == '__main__':
    """
    How to run the program (example):
    $> CURR_DIR = `implementation/src/`
    $> python main.py ../input/121/121-HU.in ../input/121/121-seg.in
    """

    # Grab the arguments
    args = parse_args()
    hu_mat_path = args.hu_mat_input
    hu_seg_path = args.hu_seg_input

    # Sanity checks
    if not os.path.exists(hu_mat_path) or not os.path.exists(hu_seg_path):
        print(f'`{hu_mat_path}` and `{hu_seg_path}` must be valid file paths!')
        sys.exit()

    # Parse the matrices
    hu_mat = file_to_matrix(hu_mat_path)
    hu_seg = file_to_matrix(hu_seg_path)

    # Check if the ROI is big or small
    _, hu_seg_hull = generate_convex_hull(hu_seg)
    if hu_seg_hull.volume > LIVER_VOLUME_THRESHOLD:
        big_liver()
    else:
        small_liver()
