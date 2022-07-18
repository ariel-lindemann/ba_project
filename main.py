import cv2
from cv2 import threshold
from cv2 import THRESH_BINARY
import numpy as np
import defaults

import detect
from calibration.camera_calibration import calibrate_camera, undistort, is_calibrated
from alignment.alignment import align
from positioning import assess_position

from defaults import TOLERANCE, CAMERA_NUMBER, MARKER_TYPE, PARAMS_DIR, ALIGNMENT_TEMPLATE_IMG_PATH, STD_WAIT
from calibration import agv_pattern, agv_info
from cluster import cluster_dbscan, _threshold_img, code_masks, draw_contours #TODO remove protected method

from exceptions import InvalidBarcodeException

from cluster import masked_img

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

    force_recalibration = False
    camera_calibrated = is_calibrated()

    if not camera_calibrated or force_recalibration:
        #calibrate_camera(with_video=True)
        print('Calibration sucessful')

    cal_mtx = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    dist_mtx = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    template_image = cv2.imread(ALIGNMENT_TEMPLATE_IMG_PATH)
#    template_points, template_data = detect.find_markers(template_image, marker_type)[0]

    while True:
        success, img = cap.read()

        if not success:
            raise RuntimeError('Image capture unsuccessful')


        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        threshold_img = _threshold_img(img)

        #undistorted_img = undistort(img, cal_mtx, dist_mtx, alpha=0)

        try: 
            data, found = detect.find_markers(img, marker_type='aztec')  # boxes and IDs of found markers
        except InvalidBarcodeException:
            found = []
            data = 'Invalid code'


        # position_correct = assess_position(REQUIRED_POSITION, found[0])
        position_box_color = (0, 0, 255) #TODO
        # if position_correct: position_box_color=(0, 255, 0)
        #cv2.polylines(img, [REQUIRED_POSITION], isClosed=True, color=position_box_color)
        cv2.putText(img, f'Decoded: {data}', org=(100, 600), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(0,255,0))

        # aligned_img = align(img, template_image , found, template_points)

        # cv2.resize(img, (undistorted_img.shape[0], undistorted_img.shape[1]), dst=img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5)
        thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1]
        masked = masked_img(thresh)

        draw_contours(img, code_masks(img)[0])

        #img_concat = np.concatenate((img, thresh, masked), axis=0)
        cv2.imshow('Aligned', img)
        print(data, found)

        if cv2.waitKey(STD_WAIT) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
