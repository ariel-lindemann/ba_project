import numpy as np
import points_utils as pu
from scipy.spatial import distance as dist

from defaults import TOLERANCE
from exceptions import TooFewPointsException
from scaling import scale_parameter
from detect import find_codes


#TODO find a way to use (only once)
def get_position_points(img):
    _, unsorted_positions = find_codes(img)
    sorted_positions = pu.handle_position_points(unsorted_positions)
    return sorted_positions


def assess_position_abs_distances(actual, required):
    ''' 
    distance betweeen corresponding points
    '''
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


#TODO move to process results
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


#TODO move to process results
def _scale_points(img, points):
    scale = scale_parameter(img)
    points *= scale
    return points
