import calibration.agv_pattern as pat
import os
import cv2
import json
from calibration.agv_info import AgvInfo

def create_pattern(img_path='tests/test_data/alignment_template.jpg'):
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass
    return pat.create_agv_template(agv, img_path=img_path)

def test_agv_pattern_created():
    img_path = 'tests/test_data/alignment_template.jpg'
    create_pattern(img_path)
    assert os.path.exists(img_path)


def test_agv_pattern_correct():
    img = create_pattern()
    detector = cv2.QRCodeDetector()
    data, _, _  = detector.detectAndDecode(img)
    for d in data:
        agv = json.loads(d)
        assert agv['serial_no'] == 'test'
        