import numpy as np

from scipy.spatial import distance as dist
from calibration.agv_info import AgvInfo
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
    # same for right-most
    right_most = right_most[np.argsort(right_most[:, 1]), :]
    (tr, br) = right_most

    return np.array([tl, tr, br, bl], dtype=np.int32)


def zx_position_to_np(position):
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
        np_points = zx_position_to_np(p)
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


def centers_coordinates_from_agv_info(agv_info: AgvInfo, pattern_size=100):
    '''
    returns 4 points corresponding to the centers of the codes on the AGV. 
    They are ordered clockwise (starting from top-left)
    '''
    length = agv_info.length
    width = agv_info.width
    half_pattern_size = pattern_size//2
    coordinates = np.ones((4, 3), dtype=np.float32)

    # x coordinates from left to right
    coordinates[0:4:3, 0] = half_pattern_size
    coordinates[1:3, 0] = length - half_pattern_size
    # y coordinates from top to bottom
    coordinates[0:2, 1] = half_pattern_size
    coordinates[2:4, 1] = width - half_pattern_size
    # z coordinates
    coordinates[:, 2] = 0

    return coordinates


def corner_coordinates_from_agv_info(agv_info: AgvInfo, pattern_size=100):
    '''
    returns 16 points corresponding to the corners of the codes on the AGV. 
    They are ordered recursively clockwise (starting from top-left)
    '''
    length = agv_info.length
    width = agv_info.width

    coordinates = np.ones((4, 4, 3))

    # x coordinates from left to right
    coordinates[0:4:3, 0:4:3, 0] = 0
    coordinates[0:4:3, 1:3, 0] = pattern_size
    coordinates[1:3, 0:4:3, 0] = length - pattern_size - 1
    coordinates[1:3, 1:3, 0] = length  - 1
    # y coordinates from top to bottom
    coordinates[0:2, 0:2, 1] = 0
    coordinates[0:2, 2:4, 1] = pattern_size
    coordinates[2:4, 0:2, 1] = width - pattern_size - 1
    coordinates[2:4, 2:4, 1] = width - 1
    # z coordinates
    coordinates[:, :, 2] = 0

    coordinates = coordinates.reshape((16, 3))
    return coordinates


def compute_pairwise_distances(points1: np.ndarray, points2: np.ndarray):
    '''
    points1: 4x2 ndarray
    points2: 4x2 ndarray
    '''
    D = dist.cdist(points1, points2, 'euclidean')
    # we don't need all the distances
    distances = np.diagonal(D)
    return distances
