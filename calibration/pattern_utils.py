import cv2
import pyqrcode
import numpy as np
from math import sqrt
import zxingcpp as zx


def place_pattern_on_img(pattern, img, pos):
    offset_x = pos[0]
    offset_y = pos[1]

    pattern_length = pattern.shape[0]
    pattern_width = pattern.shape[1]

    img[offset_x:offset_x+pattern_length,
        offset_y:offset_y+pattern_width] = pattern

    return img


def create_code(data, size = 1000, code_type = 'aztec'):
    if code_type == 'qr':
        return _create_qr_code(data, size)
    elif code_type == 'aztec':
        return _create_aztec_code(data, size)
    else:
        raise RuntimeError(f'{code_type} is not a supported code type')


def _create_qr_code(data, size):
    img = zx.write_barcode(zx.BarcodeFormat.QRCode, data, width=size, height=size) 
    return img

def _create_aztec_code(data, size):
    img = zx.write_barcode(zx.BarcodeFormat.Aztec, data, width=size, height=size) 
    return img
