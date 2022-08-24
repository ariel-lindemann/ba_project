# TODO move to different module?
import cv2
import numpy as np
import zxingcpp as zx
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
    tl_coordinates = [border, border]
    tr_coordinates = [width - margin-border, border]
    bl_coordinates = [border, length - margin-border]
    br_coordinates = [width - margin - border, length - margin - border]

    # draw the corner codes
    place_pattern_on_img(corner_codes['TL'], template, tl_coordinates)
    place_pattern_on_img(corner_codes['TR'], template, tr_coordinates)
    place_pattern_on_img(corner_codes['BL'], template, bl_coordinates)
    place_pattern_on_img(corner_codes['BR'], template, br_coordinates)

    return template


def create_agv_template(agv_info: AgvInfo, pattern_size=100, code_type='aztec', border=0, dpi=5, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, write_file=True):
    '''
    Creates the template for aligning the captured image and saves it.

    Parameters
    ----------

    agv_info: AgvInfo
        The information in the codes whitch will be placed in the corners.

    pattern_size: int, optional
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
            pattern_size * SCALING_FACTOR))  # TODO why 100?
        corner_codes.update([(c, c_code)])

    length = round(agv_info.length * SCALING_FACTOR)
    width = round(agv_info.width * SCALING_FACTOR)

    # margin such that the corners of the square match the image corners
    margin = round(pattern_size * SCALING_FACTOR)

    #TODO better name for variable `margin`
    template = _place_corner_codes(
        corner_codes, width, length, margin, border=border)
    # save template to disk
    if write_file:
        cv2.imwrite(img_path, template)
    return template
