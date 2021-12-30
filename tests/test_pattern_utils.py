import unittest
import cv2
from calibration.pattern_utils import create_code


class TestPatterns(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    img = None

    def test_create_code(self):
        data = 'test_string'
        img_size = 100
        img = create_code(data, img_size)
        assert(img.shape[0] == img.shape[1])  # img should be square
        assert(img.shape[0] == img_size)  # should be the specified size

    def test_code_correctness(self):
        '''
        Is the decoded data the same as the encoded
        '''
        data = 'test_string'
        img = create_code(data)
        detector = cv2.QRCodeDetector()
        detected, _, _ = detector.detectAndDecode(img)
        assert(data == detected)

    # TODO test agv code


if __name__ == '__main__':
    unittest.main()
