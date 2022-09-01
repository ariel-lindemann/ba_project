import calibration.agv_pattern as pat
import os
import json
import zxingcpp as zx
from calibration.agv_info import AgvInfo


def create_pattern(img_path='tests/test_data/alignment_template.jpg', write_file=True, border=0):
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    if write_file:
        try:
            os.remove(img_path)
        except FileNotFoundError:
            pass

    return pat.create_agv_template(agv, pattern_img_size=35, img_path=img_path, write_file=write_file, code_type='datamatrix', border=border)


def test_agv_pattern_created():
    img_path = 'tests/test_data/alignment_template.jpg'
    create_pattern(img_path, border=500)
    assert os.path.exists(img_path)


def test_agv_pattern_correct():
    img = create_pattern(write_file=False)
    #TODO multiple detection
    data = zx.read_barcode(img).text
    if not data:
        assert False, 'No data detected'
    for d in data:
        agv = json.loads(d)
        assert agv['serial_no'] == 'test'#TODO
