import cv2
import os
import calibration.pattern_utils as pu
from calibration.agv_info import AgvInfo


def test_create_code():
    data = 'test_string'
    img_size = 100
    img = pu.create_code(data, img_size, code_type='qr')
    assert(img.shape[0] == img.shape[1])  # img should be square
    assert(img.shape[0] == img_size)  # should be the specified size


def test_code_correctness():
    '''
    Is the decoded data the same as the encoded
    '''
    data = 'test_string'
    img = pu.create_code(data, code_type='qr')
    detector = cv2.QRCodeDetector()
    detected, _, _ = detector.detectAndDecode(img)
    assert(data == detected)


def test_create_aztec_code_image():
    data = 'test_string'
    img = pu._create_aztec_code_img(data)
    img.save('aztec.png')
    assert img


def test_create_aztec_code_array():
    img_path = 'tests/test_data/aztec_array.png'
    data = 'test_data'
    agv = AgvInfo(50, 50, 9, 2, 2, 'test')
    img = pu._create_aztec_code_array(data)
    cv2.imwrite(img_path, img)
    assert (os.path.exists(img_path))
