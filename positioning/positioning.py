import numpy as np
from scipy.spatial import distance as dist

from defaults import TOLERANCE
from exceptions import TooFewPointsException
from segment import segment_positions, scale_parameter


def get_position_points(img):
    unsorted = segment_positions(img=img)
    return _handle_position_points(unsorted)

def assess_position_abs_distances(img, required):
    ''' 
    distance betweeen corresponding points
    '''
    actual = get_position_points(img)
    # TODO handle TooFewPointsException
    distances = _compute_pairwise_distances(required, actual)

    return distances

def _compute_pairwise_distances(points1: np.ndarray, points2: np.ndarray):
    '''
    points1: 4x2 ndarray
    points2: 4x2 ndarray
    '''
    D = dist.cdist(points1, points2, 'euclidean')
    # we don't need all the distances
    distances = np.diagonal(D)
    return distances


def _handle_position_points(points):
    # if len(points) == 3:
    # if one point is missing we can infer it
    # using the remaining 3
    # TODO  points = _add_fourth_point(points)
    if len(points) <= 2:
        raise TooFewPointsException

    sorted_points = _sort_points(points)
    return sorted_points


def pos_to_dict(points):
    '''
    labels sorted points. Works for distances as well.
    Only works for 4 elements
    '''
    if len(points) != 4:
        raise TooFewPointsException
    else:
        tl = points[0]
        tr = points[1]
        br = points[2]
        bl = points[3]
        return {'TL':tl, 'TR':tr, 'BR': br, 'BL': bl}


def _sort_points(points):
    # sort points based on x coordinates
    sorted_x = points[np.argsort(points[:, 0]), :]

    left_most = sorted_x[:2, :]
    right_most = sorted_x[2:, :]

    # sort the left-most coordinates according to y coordinates
    # so we can grab the top-left and bottom-left points
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    (tl, bl) = left_most

    # now that we have the TL coordinate, use it
    # to calculate the Euclidean distance between
    # TL and right-most points
    D = dist.cdist(tl[np.newaxis], right_most, 'euclidean')[0]
    # by the Pythagorean theorem, the point with the
    # largest distance will be the BR point
    (br, tr) = right_most[np.argsort(D)[::-1], :]

    return np.array([tl, tr, br, bl], dtype='float32')


def _zx_position_to_np(position):
    '''
    convert points from zx.position to np array
    '''
    np_points = np.zeros((4, 2))
    #TODO in order tl, tr, br, bl
    zx_tl = position.top_left
    zx_tr = position.top_right
    zx_br = position.bottom_right
    zx_bl = position.bottom_left

    zx = [zx_tl, zx_tr, zx_br, zx_bl]

    for (i, p) in enumerate(zx):
        np_points[i, 0] = p.x
        np_points[i, 1] = p.y

    return np_points


def _zx_position_centroids(points):
    np_points = _zx_position_to_np(points)
    centroid = _calculate_centroid(np_points)
    return centroid


def _calculate_centroid(points):
    '''
    calculate the centroid from a given set of points.
    Points should be passed as `n x 2`-shaped np arrays (`n` being the number of points)
    '''
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    centroid = (sum(x) // len(points), sum(y) // len(points))
    return centroid


def scale_points(img, points):
    scale = scale_parameter(img)
    points *= scale
    return points
