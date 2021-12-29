import cv2
import pyqrcode
import numpy as np
from math import sqrt


def place_pattern_on_img(pattern, img, pos):
    offset_x = pos[0]
    offset_y = pos[1]

    pattern_length = pattern.shape[0]
    pattern_width = pattern.shape[1]

    img[offset_x:offset_x+pattern_length,
        offset_y:offset_y+pattern_width] = pattern

    return img


def create_code(data, size=100):
    '''
    Creates a QR code representation of the given data as a numpy array.

    Parameters
    ----------

    data:
        the data to be encoded

    size: optional
        the length of the QR code square in pixels
    '''
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
