import calibration.agv_pattern as pat
import os
from calibration.agv_info import AgvInfo

def test_agv_pattern_created():
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    img_path = 'tests/test_data/alignment_template.jpg'
    pat.create_agv_template(agv, img_path=img_path)
    assert os.path.exists(img_path)