from commons import *

from scipy.spatial import ConvexHull, convex_hull_plot_2d
from scipy.ndimage import binary_fill_holes

from matplotlib.path import Path

from skimage import measure
from skimage import morphology
from skimage import filters
from skimage import segmentation


def generate_convex_hull(img):
    """
    Generate the Convex Hull of a shape from a binary image
    Reference: https://en.wikipedia.org/wiki/Convex_hull
    """
    points = []
    for i in range(len(img)):
        for j in range(len(img[0])):
            if img[i][j] == 1:
                points.append([i, j])
    points = np.array(points)

    return points, ConvexHull(points)


def in_hull(hull, points, x, radius=25):
    """
    Check if a point `x` is inside the Hull's polygon
    radius=x: `expands` the polygon; this ensures that the liver will not end up cutted
    """
    hull_path = Path(points[hull.vertices])
    return hull_path.contains_point(x, radius=radius)


def slice_window(img, level=150, window=50):
    """ Limit the values in the interval [level - window/2, level + window/2] """
    low  = level - window / 2
    high = level + window / 2
    return img.clip(low, high)


def normalize(img, from_range_low, from_range_high):
    """ Normalize the image: translate the ranges from [a, b] to [0, 1] """
    return np.interp(img, (from_range_low, from_range_high), (0, 1))


def roi(hu_mat, hu_seg, hull_seg_contour=False, radius=25):
    """
    This function generates the Region of interest (ROI) on the image `hu_mat`
    We can perfom the crop operation on the `Hull polygon` or using the `doctor segmentation`
    """
    if hull_seg_contour == False:
        points, hull = generate_convex_hull(hu_seg)
    else:
        points = measure.find_contours(hu_seg, 0.95)[0]
        hull = ConvexHull(points)

    roi = np.zeros((len(hu_mat), len(hu_mat[0])))
    for i in range(len(hu_mat)):
        for j in range(len(hu_mat[0])):
            if not in_hull(hull, points, (i, j), radius):
                roi[i][j] = 0
            else:
                roi[i][j] = hu_mat[i][j]

    return roi


def binarize(img, threshold=0.5):
    """ Binarize an image using a `threshold_confidence` """
    return np.array([[0 if el < threshold else 1 for el in row] for row in img])


def remove_small_objects(img, min_size=20, ret_mask=False):
    """ Make a mask of small objects and remove those objects from the original `img` """
    if len(np.unique(img)) != 2:
        img = binarize(img)

    img_bool = np.array(img, bool)
    mask = ~morphology.remove_small_objects(img_bool, min_size).astype(int)
    if ret_mask:
        return ~mask
    return img & mask


def morphology_dilation(img):
    """ Perform a morphology `dilation` on the given `img` """
    return morphology.binary_dilation(img)


def morphology_erosion(img):
    """ Perform a morphology `erosion` on the given `img` """
    return morphology.binary_erosion(img)


def diameter_opening(img):
    """ Perform a morphology `diameter opening` on the given `img` """
    return morphology.diameter_opening(img, diameter_threshold=4, connectivity=2)


def morphology_area_opening(img, area_threshold=10):
    """ Perform a morphology `area opening` on the given `img` """
    return morphology.area_opening(img, area_threshold)


def morphology_area_closing(img, area_threshold=10):
    """ Perform a morphology `area closing` on the given `img` """
    return morphology.area_closing(img, area_threshold)


def remove_small_pixels(img, min_size=10):
    """ Remove small objects (size < `min_size`) from the given `image` """
    return morphology.remove_small_objects(img.astype(bool), min_size).astype(int)


def sobel(img):
    """
    Perform an edge detection using the Sobel filter
    Reference: https://en.wikipedia.org/wiki/Sobel_operator
    """
    return filters.sobel(img)


def fill_holes(img):
    """ Fill the holes (black pixels surrounded by white pixels) in a given `img` """
    return binary_fill_holes(img)


def get_snake(img, hu_seg):
    """ Compute the `active contour` starting from the `hu_seg` points """
    contour_seg = measure.find_contours(hu_seg, 0.95)[0]
    return segmentation.active_contour(filters.gaussian(img, 3, preserve_range=False),
                                       contour_seg, alpha=0.001, beta=200, gamma=0.01, w_edge=3)

def active_contour(img, hu_seg):
    """
    Perform an `active contour` model starting from the `hu_seg` points and
    generate a mask (binary image) using the converged (optimised) `snake` points
    Reference: https://en.wikipedia.org/wiki/Active_contour_model
    """
    snake = get_snake(img, hu_seg)
    snake_path = Path(snake)

    liver_mask = np.zeros((len(img), len(img[0])))
    for i in range(len(liver_mask)):
        for j in range(len(liver_mask[0])):
            if snake_path.contains_point((i, j)):
                liver_mask[i][j] = 1
            else:
                liver_mask[i][j] = 0

    return liver_mask
