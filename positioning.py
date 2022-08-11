import numpy as np
from scipy.spatial import distance as dist

from defaults import TOLERANCE
from exceptions import TooFewPointsException
from segment import segment_positions

# TODO rename


def assess_position_distances(img, required, tolerance=TOLERANCE):
    # distance betweeen corresponding points
    actual = segment_positions(img)
    # order points
    actual = handle_position_points(actual)
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


def handle_position_points(points):
    # if len(points) == 3:
    # if one point is missing we can infer it
    # using the remaining 3
    # TODO  points = _add_fourth_point(points)
    if len(points) <= 2:
        raise TooFewPointsException

    sorted_points = _sort_points(points)
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

    return np.array([tl, tr, br, bl], dtype='float32')
