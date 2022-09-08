import cv2
import numpy as np
import points_utils as pu

from defaults import PARAMS_DIR


def get_simple_perspective_transform(obj_coordinates, img_coordinates):
    pu._sort_points(obj_coordinates)
    pu._sort_points(img_coordinates)

    src = obj_coordinates.astype(np.float32)
    dst = img_coordinates.astype(np.float32)
    return cv2.getPerspectiveTransform(src, dst)


def _distances_with_transform(required_pos, detected_pos, transform):
    req_transformed = cv2.transform(required_pos, transform)
    detected_transformed = cv2.transform(detected_pos, transform)
    distances = pu.compute_pairwise_distances(req_transformed, detected_transformed)
    return distances
    # TODO test
    #


def perspective_transform(img_coordinates, obj_coordinates, camera_matrix=None, dist_coeffs=None):
    if not camera_matrix:
        camera_matrix = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    if not dist_coeffs:
        dist_coeffs = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    retval, rvec, tvec = cv2.solvePnP(obj_coordinates, img_coordinates, camera_matrix, dist_coeffs)
    # TODO


def transform_points(points, transformation_matrix):
    '''
    transforms an array of `n` 2d points given a `3x3` transformation matrix
    '''
    points = points.reshape((-1, points.shape[0], points.shape[1]))
    points = points.astype(np.float32)
    transformed_points = cv2.perspectiveTransform(points, transformation_matrix)
    transformed_points = transformed_points[0].astype(np.int32)
    return transformed_points
