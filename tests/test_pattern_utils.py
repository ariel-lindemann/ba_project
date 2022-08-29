import cv2
import os
import calibration.pattern_utils as pu
import zxingcpp as zx
from calibration.agv_info import AgvInfo


def test_create_code():
    data = 'test_string'
    img_size = 200
    img = pu.create_code(data, img_size, code_type='qr')
    assert(img.shape[0] == img.shape[1])  # img should be square
    assert(img.shape[0] == img_size)  # should be the specified size


def test_code_correctness_aztec():
    '''
    Is the decoded data the same as the encoded
    '''
    data = 'test_string'
    img = pu.create_code(data, code_type='aztec')
    detected = zx.read_barcode(img).text

    assert(data == detected)


def test_code_correctness_qr():
    '''
    Is the decoded data the same as the encoded
    '''
    data = 'test_string'
    img = pu.create_code(data, code_type='qr')
    detected = zx.read_barcode(img).text

    assert(data == detected)


def test_create_aztec_code_array():
    img_path = 'tests/test_data/aztec_array.png'
    data = 'test_data'
    agv = AgvInfo(50, 50, 9, 2, 2, 'test').to_json()
    img = pu.create_code(agv, 100, code_type='aztec')
    cv2.imwrite(img_path, img)
    assert (os.path.exists(img_path))
