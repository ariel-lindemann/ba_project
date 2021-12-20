import cv2
from numpy.core.fromnumeric import shape
import cv2.aruco as aruco
import numpy as np

from defaults import DEFAULT_MARKER_SIZE
from calibration.calibration_pattern import AGV_info, json_to_agv_info

def find_aruco_markers(img, marker_size=DEFAULT_MARKER_SIZE, total_markers=250, draw=True):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_parameters = aruco.DetectorParameters_create()

    # store bounding boxes, IDs and rejected
    b_boxes, ids, rejected = aruco.detectMarkers(img_gray, aruco_dict, parameters=aruco_parameters)

    if draw:
        aruco.drawDetectedMarkers(img, b_boxes, ids)

    # TODO reshape b_boxes and ids into one array
    # found = np.zeros((len(ids), 4, 2))
    b_boxes = np.asarray(b_boxes)
    #b_boxes.reshape((b_boxes.shape[0] ,b_boxes.shape[2] , b_boxes.shape[3]))

    """"
    ids_dict = {}
    for i in range(len(ids)):
        ids_dict[i] = ids[i]


        # TODO
    """
    #found = np.asarray([b_boxes, ids])

    return [b_boxes, ids]


def decode_qr(img):
    detector = cv2.QRCodeDetector()
    data, found,  = detector.detectAndDecode(img)

    return data, found

def decode_agv_info(img):
    data, found = decode_qr(img)

    for i in data:
        i = json_to_agv_info(i)

    return data, found

def find_markers(img, marker_type):
    data = []
    found = []

    if marker_type == 'aruco':
        found = find_aruco_markers(img)
    elif marker_type == 'qr':
        data, found = decode_qr(img)
    else:
        # TODO exception
        print(f'{marker_type} not a valid marker type!')

    return data, found
