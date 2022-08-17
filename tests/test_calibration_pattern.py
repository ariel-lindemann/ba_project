import json
import calibration.calibration_pattern as cal
import os
import zxingcpp as zx
from calibration.agv_info import AgvInfo
from defaults import DATA_DIR, CALIBRATION_IMGS_FORMAT


def create_pattern(img_path='tests/test_data/alignment_template.jpg', write_file=True):
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    if write_file:
        try:
            os.remove(img_path)
        except FileNotFoundError:
            pass
    return cal.create_pattern(agv, img_path=img_path, write_file=write_file)


def test_create_chess_board_correct_size():
    x = 5
    y = 5
    scale = 100
    chessboard_shape = cal.create_chess_board(x, y, scale).shape
    assert chessboard_shape[0] == x * \
        scale and chessboard_shape[1] == y * scale


def test_pattern_is_created():
    img_path = 'tests/test_data/calibration_pattern.jpg'
    create_pattern(img_path)
    assert os.path.exists(img_path)

def test_pattern_correctness():
    img = create_pattern(write_file=False)
    data = zx.read_barcode(img).text
    if not data:
        assert False, 'No data detected'
    else:
        agv = json.loads(data)
        assert agv == data

