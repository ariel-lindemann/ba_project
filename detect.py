import cv2
from numpy.core.fromnumeric import shape
import cv2.aruco as aruco
import numpy as np
import zxingcpp as zx
import segment as seg
import detect

from defaults import DEFAULT_MARKER_SIZE
from calibration.agv_info import json_to_agv_info
from segment import image_segments

from exceptions import InvalidBarcodeException


def find_aruco_markers(img, marker_size=DEFAULT_MARKER_SIZE, total_markers=250, draw=True):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_parameters = aruco.DetectorParameters_create()

    # store bounding boxes, IDs, ignore rejected
    b_boxes, ids, = aruco.detectMarkers(
        img_gray, aruco_dict, parameters=aruco_parameters)

    if draw:
        aruco.drawDetectedMarkers(img, b_boxes, ids)

    b_boxes = np.asarray(b_boxes)

    return ids, b_boxes


def decode(img):
    '''
    returns a 'zxingcpp.Result' object
    '''
    #TODO multiple detection
    results = zx.read_barcode(img)
    if not results.valid:
        raise InvalidBarcodeException('Could not read barcode')
    return results


def decode_agv_info(img):
    results = decode(img)
    #TODO needs to be changed (single responsibility)
    # we need the raw data as well as agv
    data = [results.text]
    found = [results.position]

    agv_data = []

    for i in data:
        agv_data.append(json_to_agv_info(i))

    return data, found


def find_markers(img, marker_type):
    data = []
    found = []

    results = decode(img)
    # TODO exception

    data = [results.text]
    found = [results.position]


    return data, found


def detected_results(img, with_threshold=False):
    results = []

    for s in seg.image_segments(img):
        if with_threshold:
            s = cv2.adaptiveThreshold(cv2.cvtColor(s, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5)

        try:
            results.append(detect.decode(s))
        except InvalidBarcodeException:
            pass

    return results


def find_multiple(img):
    segments = seg.image_segments(img)
    
    results = []
    #TODO