import numpy as np

from defaults import TOLERANCE

# TODO fix
def assess_position(required, actual, tolerance=TOLERANCE):
    if required.shape != actual.shape or actual:
        return False

    for i in range(required.size):
        if required[i] - actual[i] > tolerance:
            return False

    return True


def distance(point_a, point_b):
    square = np.square(point_a - point_b)
    sum_square = np.sum(square)
    distance = np.sqrt(sum_square)
    return distance

def top_left(img_points):
    min_distance = np.integer.max
    origin = np.array([0,0])
    top_left_point = np.array()

    for point in img_points:
        if distance(point, origin) < min_distance : top_left_point = point

    return top_left_point