import calibration.agv_info as agvi
import defaults as d
import json


def test_agv_to_json():
    agv = agvi.AgvInfo(d.DEFAULT_AGV_LENGTH, d.DEFAULT_AGV_WIDTH,
                       d.DEFAULT_AGV_HEIGHT, 50, 50, 'test', 'LL')
    length = agv.length
    serial_no = agv.serial_no
    agv_json = agv.to_json()
    agv_dict = json.loads(agv_json)
    assert agv_dict['length'] == length
    assert agv_dict['serial_no'] == serial_no


def test_json_to_agv_info():
    agv = agvi.AgvInfo(d.DEFAULT_AGV_LENGTH, d.DEFAULT_AGV_WIDTH,
                       d.DEFAULT_AGV_HEIGHT, 50, 50, 'test', 'LL')
    agv_json = agv.to_json()
    decoded_agv = agvi.json_to_agv_info(agv_json)
    assert agv == decoded_agv
