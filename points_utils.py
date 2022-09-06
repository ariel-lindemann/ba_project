import numpy as np

from scipy.spatial import distance as dist
from exceptions import TooFewPointsException

def handle_position_points(points):
    # if len(points) == 3:
    # if one point is missing we can infer it
    # using the remaining 3
    # TODO  points = _add_fourth_point(points)
    # TODO adapt to ndarray points ?
    if len(points) <= 2:
        raise TooFewPointsException

    sorted_points = _sort_points(np.array(points))
    return sorted_points


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

    return np.array([tl, tr, br, bl], dtype=np.int32)


def _zx_position_to_np(position):
    '''
    convert points from zx.position to np array
    '''
    np_points = np.zeros((4, 2), np.int32)

    zx_tl = position.top_left
    zx_tr = position.top_right
    zx_br = position.bottom_right
    zx_bl = position.bottom_left

    zx = [zx_tl, zx_tr, zx_br, zx_bl]

    for (i, p) in enumerate(zx):
        np_points[i, 0] = p.x
        np_points[i, 1] = p.y

    return np_points


def zx_positions_centroids(positions):
    '''
    gives the centroids for a list of `zxingcpp.Position`
    '''
    centroids = np.zeros((len(positions), 2), np.int32)
    for (i, p) in enumerate(positions):
        np_points = _zx_position_to_np(p)
        centroids[i] = _calculate_centroid(np_points)
    return centroids


def _calculate_centroid(points):
    '''
    calculate the centroid from a given set of points.
    Points should be passed as `n x 2`-shaped np arrays (`n` being the number of points)
    '''
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    centroid = (sum(x) // len(points), sum(y) // len(points))
    return centroid
