# TODO move to different module?
import cv2
import cv2.aruco as aruco
import numpy as np
from calibration.pattern_utils import create_code, place_pattern_on_img
from calibration.agv_info import AgvInfo

from defaults import ALIGNMENT_TEMPLATE_IMG_PATH


def _create_corner_code(agv_info: AgvInfo, corner, code_type='qr', size=100):
    '''
    Wrapper for `pattern_utils.create_code()`. Adds corner information to the code.
    '''
    agv_info.corner = corner
    agv_json = agv_info.to_json()
    code = create_code(agv_json, size=size, code_type=code_type)
    return code


def _place_corner_codes(corner_codes, width, length, margin, border=0):
    template = np.zeros([width, length], dtype=np.uint8)
    # turn image white
    template[:, :] = 255
    # coordinates for each corner
    bl_coordinates = [border, border]
    br_coordinates = [width - margin - border, border]
    tl_coordinates = [border, length - margin-border]
    tr_coordinates = [width - margin - border, length - margin - border]

    # draw the corner codes
    place_pattern_on_img(corner_codes['TL'], template, tl_coordinates)
    place_pattern_on_img(corner_codes['TR'], template, tr_coordinates)
    place_pattern_on_img(corner_codes['BL'], template, bl_coordinates)
    place_pattern_on_img(corner_codes['BR'], template, br_coordinates)

    return template


def _create_template(corner_patterns, pattern_img_size=100, border=0, dpi=5, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, write_file=True, width=380, length=560):

    SCALING_FACTOR = dpi * 3.9370079
    length = round(length * SCALING_FACTOR)
    width = round(width * SCALING_FACTOR)

    #TODO better name for variable `margin`
    # margin such that the corners of the square match the image corners
    margin = round(pattern_img_size * SCALING_FACTOR)

    template = _place_corner_codes(corner_patterns, width, length, margin, border=border)
    if write_file:
        cv2.imwrite(img_path, template)
    return template


def create_agv_template(agv_info: AgvInfo, pattern_img_size=100, code_type='aztec', border=0, dpi=5, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, write_file=True):
    '''
    Creates the template for aligning the captured image and saves it.

    Parameters
    ----------

    agv_info: AgvInfo
        The information in the codes whitch will be placed in the corners.

    pattern_img_size: int, optional
        Length of the QR code square in pixels.

    extra_margin: int, optional
        Add an extra margin on the sides. Length in pixels

    img_path: str, optional
        The path in which the image will be saved. Default as specified in config.

    dpi: int, optional
        Pixel density on the image

    write_file: bool, optional
        Should the file be written to disk
    '''

    SCALING_FACTOR = dpi * 3.9370079

    corners = ['TL', 'TR', 'BL', 'BR']
    corner_codes = {}

    for c in corners:
        c_code = _create_corner_code(agv_info, c, code_type=code_type, size=round(
            pattern_img_size * SCALING_FACTOR))  # TODO why 100?
        corner_codes.update([(c, c_code)])

    template = _create_template(corner_codes, pattern_img_size, border, dpi, img_path, write_file, agv_info.width, agv_info.length)

    return template


def create_aruco_template(marker_size, total_markers=250, pattern_img_size=100, border=0, dpi=5, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, write_file=True, width=380, length=560):
    '''
    Creates the template for aligning the captured image and saves it.

    Parameters
    ----------

    marker_size: int
        Size of marker in bits

    total_markers: int, optional
        Total number of ArUco markers

    pattern_img_size: int, optional
        Length of the QR code square in pixels.

    extra_margin: int, optional
        Add an extra margin on the sides. Length in pixels

    img_path: str, optional
        The path in which the image will be saved. Default as specified in config.

    dpi: int, optional
        Pixel density on the image

    write_file: bool, optional
        Should the file be written to disk
    '''

    #TODO
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    aruco_dict = aruco.Dictionary_get(key)

    corners = ['TL', 'TR', 'BL', 'BR']
    corner_markers = {}

    for (i, label) in enumerate(corners):
        marker_img = np.zeros((pattern_img_size, pattern_img_size))
        marker = aruco.DrawMarker(aruco_dict, i, pattern_img_size, marker_img)
        corner_markers.update([(label, marker)])

    template = _create_template(corner_markers, pattern_img_size, border, dpi, img_path, write_file, width, length)

    return template