import numpy as np
import points_utils as pu
import positioning.perspective_transform as p_tran

from defaults import TOLERANCE
from exceptions import TooFewPointsException
from scaling import scale_parameter
from detect import find_codes


#TODO find a way to use (only once)
def get_data_and_position_points(img):
    data, unsorted_positions = find_codes(img)
    try:
        sorted_positions = pu.handle_position_points(unsorted_positions)
    except TooFewPointsException:
        sorted_positions = np.array(unsorted_positions) #TODO pu.handle_too_few_points(unsorted_positions, data) 
    return data, sorted_positions


def calculate_abs_distances_in_mm(actual, required, data):
    ''' 
    distance betweeen corresponding points.
    '''
    # TODO handle TooFewPointsException
    actual = get_transformed_points(actual, data)
    mm_per_pixel = _calculate_mm_per_pixel(actual, required)
    actual = mm_per_pixel * actual.astype(np.float64)
    distances = pu.compute_pairwise_distances(required, actual)

    return distances


#TODO affine transform

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


def get_transformed_points(detected_points, detected_data):
    '''
    get position of the AGV with regard to its plane
    '''
    agv_coordinates = pu.centers_coordinates_from_agv_info(detected_data)[:2, :] # only 2d needed
    M = p_tran.get_simple_perspective_transform(
        detected_points, agv_coordinates)
    transformed = p_tran.transform_points(detected_points, M)
    return transformed


def _calculate_mm_per_pixel(detected_points, agv_coordinates):
    '''
    gives the metric of mm per pixels. Expects detected points (transformed),  
    agv corner coordinates. Points MUST be sorted clockwise beginning at TL
    '''
    agv_length=agv_coordinates[1, 0] - agv_coordinates[0, 0]        # mm
    measured_length=detected_points[1, 0] - detected_points[0, 0]   # pixels

    mm_per_pixel = agv_length/measured_length
    return mm_per_pixel