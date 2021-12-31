# TODO move to different module?
import cv2
import numpy as np
from calibration.pattern_utils import create_code, place_pattern_on_img
from calibration.agv_info import AgvInfo

from defaults import ALIGNMENT_TEMPLATE_IMG_PATH


def _create_corner_code(agv_info: AgvInfo, corner, size=100):
    '''
    Wrapper for `pattern_utils.create_code()`. Adds corner information to the code.
    '''
    agv_info.corner = corner
    agv_json = agv_info.to_json()
    code = create_code(agv_json, size=size)
    return code


def create_agv_template(agv_info: AgvInfo, qr_code_size=100, img_path=ALIGNMENT_TEMPLATE_IMG_PATH, dpi = 5):
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
    '''

    SCALING_FACTOR = dpi * 3.9370079

    corners = ['UL', 'UR', 'LL', 'LR']
    corner_codes = {}

    for c in corners:
        c_code = _create_corner_code(agv_info, c, size = 100 * SCALING_FACTOR)
        corner_codes.update([(c, c_code)])

    length = round(agv_info.length * SCALING_FACTOR)
    width = round(agv_info.width * SCALING_FACTOR)

    template = np.zeros([width, length], dtype=np.uint8)
    # turn image white
    template[:, :] = 255

    # margin such that the corners of the square match the image corners
    margin = round(qr_code_size * SCALING_FACTOR)
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
    # save template to disk
    cv2.imwrite(img_path, template)
    return template
