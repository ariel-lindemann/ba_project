import detect
import calibration.pattern_utils as pu
from calibration.agv_info import AgvInfo, json_to_agv_info

def test_detect_qr():
    data = 'test_data'
    code = pu.create_code(data, code_type='qr')

    decoded = detect.decode_single(code).text
    
    print(code)
    assert(data == decoded)

def test_detect_aztec():
    data = 'test_data'
    img_path = 'tests/test_data/aztec_array.png'
    code = pu.create_code(data, code_type='aztec')

    decoded = detect.decode_single(code).text
    
    print(code)
    assert(data == decoded)

def test_decode_agv_info():
    agv = AgvInfo(560, 380, 200, 50, 50, 'test')
    code = pu.create_code(agv.to_json(), code_type='qr')

    decoded, found = detect.decode_agv_info(code)
    decoded_agv = json_to_agv_info(decoded[0])

    assert(decoded_agv == agv)
    
