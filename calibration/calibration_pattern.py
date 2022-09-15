import cv2
import numpy as np
from calibration.agv_info import AgvInfo
import calibration.pattern_utils as pattern_utils

from defaults import CALIBRATION_IMGS_PATH, CALIBRATION_CORNERS_X, CALIBRATION_CORNERS_Y


def create_pattern(agv_data: AgvInfo, img_shape=[2100, 2970], chessboard_corners=[CALIBRATION_CORNERS_X, CALIBRATION_CORNERS_Y], img_path=CALIBRATION_IMGS_PATH, write_file=True, code_type='qr'):
    agv_json = agv_data.to_json()
    qr_code = pattern_utils.create_code(agv_json, code_type=code_type)
    img = np.ones((img_shape[0], img_shape[1]), np.uint8)
    # start with a white image
    img[:] = 255

    chessboard = create_chess_board(
        chessboard_corners[0], chessboard_corners[1], 200)

    pattern_utils.place_pattern_on_img(qr_code, img, [0, 0])
    pattern_utils.place_pattern_on_img(
        chessboard, img, [0, int(img_shape[1]/2)])

    if write_file:
        cv2.imwrite(img_path, img)

    return img


def create_chess_board(x, y, scale):
    '''
    Create a chess beard pattern with `x*y` amount of corners. `scale` indicates the size of one square
    '''
    img = np.zeros(((y+1), (x+1)))

    width = y * scale
    height = x * scale
    # turn every 2nd pixel white
    img[::2, ::2] = 255
    img[1::2, 1::2] = 255
    # scale to desired size
    img = cv2.resize(img, (height, width), interpolation=cv2.INTER_AREA)
    return img
