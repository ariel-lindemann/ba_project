import cv2
from calibration.pattern_utils import create_code


def test_create_code():
    data = 'test_string'
    img_size = 100
    img = create_code(data, img_size)
    assert(img.shape[0] == img.shape[1])  # img should be square
    assert(img.shape[0] == img_size)  # should be the specified size


def test_code_correctness():
    '''
    Is the decoded data the same as the encoded
    '''
    data = 'test_string'
    img = create_code(data)
    detector = cv2.QRCodeDetector()
    detected, _, _ = detector.detectAndDecode(img)
    assert(data == detected)
