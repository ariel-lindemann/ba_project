import cv2
import numpy as np

import detect
from calibration.camera_calibration import calibrate_camera, undistort, is_calibrated
from alignment import align
from positioning import assess_position

CAMERA_NUMBER = 0
STD_WAIT = 5
MARKER_TYPE = 'aruco'
DEFAULT_MARKER_SIZE = 4
TOLERANCE = 0
PARAMS_DIR = 'camera_parameters'
TEMPLATE_IMG_PATH = 'alignment_templates/template.png'

REQUIRED_POSITION = np.array([[100, 100], [800, 100], [800, 550], [100, 550]], np.int32)


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

def main():
    cap = cv2.VideoCapture(CAMERA_NUMBER)
    marker_type = MARKER_TYPE

    camera_calibrated = is_calibrated()

    if not camera_calibrated:
        calibrate_camera()

    cal_mtx = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    dist_mtx = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    template_image = cv2.imread(TEMPLATE_IMG_PATH)
    template_points = detect.find_markers(template_image, marker_type)[0]

    while True:
        success, img = cap.read()

        undistorted_img = undistort(img, cal_mtx, dist_mtx, alpha=0)

        data, found = detect.find_markers(img, marker_type)  # boxes and IDs of found markers
        # position_correct = assess_position(REQUIRED_POSITION, found[0])
        position_box_color = (0, 0, 255)
        # if position_correct: position_box_color=(0, 255, 0)
        cv2.polylines(img, [REQUIRED_POSITION], isClosed=True, color=position_box_color)
        cv2.putText(img, f'{len(found[0])} Markers', org=(100, 600), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(0,255,0))

        # aligned_img = align(img, template_image , found, template_points)

        # cv2.resize(img, (undistorted_img.shape[0], undistorted_img.shape[1]), dst=img)
        # img_concat = np.concatenate((img, img), axis=0)
        cv2.imshow("Aligned", undistorted_img)
        print(found)

        cv2.waitKey(STD_WAIT)


if __name__ == "__main__":
    main()
