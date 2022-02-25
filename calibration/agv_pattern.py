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


def _place_corner_codes(corner_codes, width, length, margin):
    template = np.zeros([width, length], dtype=np.uint8)
    # turn image white
    template[:, :] = 255
    # coordinates for each corner
    ul_coordinates = [0, 0]
    ur_coordinates = [width - margin, 0]
    ll_coordinates = [0, length - margin]
    lr_coordinates = [width - margin, length - margin]
    # draw the corner codes
    place_pattern_on_img(corner_codes['UL'], template, ul_coordinates)
    place_pattern_on_img(corner_codes['UR'], template, ur_coordinates)
    place_pattern_on_img(corner_codes['LL'], template, ll_coordinates)
    place_pattern_on_img(corner_codes['LR'], template, lr_coordinates)

    return template


def create_agv_template(agv_info: AgvInfo, pattern_size=100, code_type = 'aztec', dpi=5, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, write_file=True):
    '''
    Creates the template for aligning the captured image and saves it.

    Parameters
    ----------

    agv_info: AgvInfo
        The information in the codes whitch will be placed in the corners.

    qr_code_size: int, optional
        Length of the QR code square in pixels.

    img_path: str, optional
        The path in which the image will be saved. Default as specified in config.

    dpi: int, optional
        Pixel density on the image

    write_file: bool, optional
        Should the file be written to disk
    '''

    SCALING_FACTOR = dpi * 3.9370079

    corners = ['UL', 'UR', 'LL', 'LR']
    corner_codes = {}

    for c in corners:
        c_code = _create_corner_code(agv_info, c, code_type=code_type, size=round(pattern_size * SCALING_FACTOR))#TODO why 100?
        corner_codes.update([(c, c_code)])

    length = round(agv_info.length * SCALING_FACTOR)
    width = round(agv_info.width * SCALING_FACTOR)

    # margin such that the corners of the square match the image corners
    margin = round(pattern_size * SCALING_FACTOR)

    template = _place_corner_codes(corner_codes, width, length, margin)
    # save template to disk
    if write_file:
        cv2.imwrite(img_path, template)
    return template
