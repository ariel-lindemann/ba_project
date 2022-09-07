from points_utils import zx_positions_centroids, zx_position_to_np
from exceptions import InvalidBarcodeException

import numpy as np


def parse_result_position(result, segment_position):
    if segment_position[0] < 0:
        raise InvalidBarcodeException

    position = result.position
    position_center = zx_positions_centroids([position])[0]
    # determine position on the image (segment postion being the UL corner of the segment)
    x = position_center[0] + segment_position[0]
    y = position_center[1] + segment_position[1]

    return (x, y)


def corners_from_result(result, segment_position):
    '''
    returns the four corner coordinates of the `zxing-cpp.Result` with respect to the original image
    '''
    if segment_position[0] < 0:
        raise InvalidBarcodeException

    points = np.zeros((4, 2))
    for (i, r) in result:
        position = r.position
        points[i*4] = zx_position_to_np(position)

    points[:][0] += segment_position[0]
    points[:][1] += segment_position[1]

    return points


def all_corners_from_results_list(results, segment_positions):
    '''
    returns all corner coordinates of the `zxing-cpp.Result` in the given list. Coordinates are described 
    with respect to the original image
    '''
    skipped = 0
    corners = np.zeros((len(results) * 4, 2))
    for (i, r) in enumerate(results):
        try:
            corners[i*4] = corners_from_result(r, segment_positions[i+skipped])
        except InvalidBarcodeException:
            skipped += 1
            corners[i*4] = corners_from_result(r, segment_positions[i+skipped])

    return corners
