import detect
import cv2
import calibration.pattern_utils as pu
from calibration.agv_info import AgvInfo

def test_detect_qr():
    data = 'test_data'
    code = pu.create_code(data, code_type='qr')

    decoded = detect.decode_qr(code).text
    
    print(code)
    assert(data == decoded)

def test_detect_aztec():
    data = 'test_data'
    img_path = 'tests/test_data/aztec_array.png'
    code = cv2.imread(img_path)

    decoded = detect.decode_aztec(code).text
    
    print(code)
    assert(data == decoded)

def test_decode_agv_info():
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    code = pu.create_code(agv.to_json(), code_type='qr')

    decoded, found = detect.decode_agv_info(code)
    decoded_agv = decoded[0]

    assert(decoded_agv == agv)
    
