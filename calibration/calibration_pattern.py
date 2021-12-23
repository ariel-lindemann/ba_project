import json
import cv2
import pyqrcode
import numpy as np

from math import sqrt
from defaults import CALIBRATION_IMGS_FORMAT, DATA_DIR, CALIBRATION_CORNERS_X, CALIBRATION_CORNERS_Y

# TODO more elegant placement


def create_pattern(agv_data, shape=[2100, 2970], chessboard_corners=[CALIBRATION_CORNERS_X, CALIBRATION_CORNERS_Y]):
    qr_code = create_code(agv_data)
    img = np.ones((shape[0], shape[1]), np.uint8)
    # start with a white image
    img[:] = 255

    chessboard = create_chess_board(
        chessboard_corners[0], chessboard_corners[1], 200)

    place_pattern_on_img(qr_code, img, [0, 0])
    place_pattern_on_img(chessboard, img, [0, int(shape[1]/2)])

    cv2.imwrite(
        f'{DATA_DIR}/calibration_pattern.{CALIBRATION_IMGS_FORMAT}', img)


def place_pattern_on_img(pattern, img, pos):
    offset_x = pos[0]
    offset_y = pos[1]

    pattern_length = pattern.shape[0]
    pattern_width = pattern.shape[1]

    img[offset_x:offset_x+pattern_length,
        offset_y:offset_y+pattern_width] = pattern

    return img


def create_code(data, size=1000):
    qr_size = size
    qr_code = pyqrcode.create(data)
    qr_code = qr_code.text()
    # remove all newlines
    qr_code = qr_code.replace('\n', '')
    # get total number of pixels (characters) from the QR Code string
    size = len(qr_code)
    # calculate image dimensions (qr code is square)
    shape = int(sqrt(size))
    qr_array = np.zeros([shape, shape], dtype='uint8')
    row = column = 0

    for char in qr_code:
        if char == '0':
            qr_array[row][column] = 255
            column = column + 1

        if char == '1':
            qr_array[row][column] = 0
            column = column + 1

        if column == shape:
            row = row + 1
            column = 0

    # scale up the QR code.
    qr_array = cv2.resize(qr_array, (qr_size, qr_size),
                          fx=0, fy=0, interpolation=cv2.INTER_AREA)
    # apply border to QR code
    # qr_array = cv2.copyMakeBorder(qr_array, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=0)

    return qr_array


def json_to_agv_info(json_data):
    '''
    Convert a JSON representation onto an `AGV_info` object
    '''
    as_dict = json.loads(json_data)
    return AGV_info(as_dict['length'], as_dict['width'], as_dict['height'], as_dict['raster_x'], as_dict['raster_y'], as_dict['serial_no'])


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


class AGV_info:
    def __init__(self, length, width, height, raster_x, raster_y, serial_no):
        self.length = length
        self.width = width
        self.height = height
        self.raster_x = raster_x
        self.raster_y = raster_y
        self.serial_no = serial_no

    def to_json(self):
        return json.dumps(self.__dict__)
