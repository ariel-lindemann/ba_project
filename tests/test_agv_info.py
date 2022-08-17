import calibration.agv_info as agvi
import defaults as d
import json


def create_agv(with_corner=True):
    if with_corner:
        return agvi.AgvInfo(d.DEFAULT_AGV_LENGTH, d.DEFAULT_AGV_WIDTH, d.DEFAULT_AGV_HEIGHT, 50, 50, 'test', 'LL')
    else:
        return agvi.AgvInfo(d.DEFAULT_AGV_LENGTH, d.DEFAULT_AGV_WIDTH, d.DEFAULT_AGV_HEIGHT, 50, 50, 'test')


def test_agv_to_json():
    agv = create_agv()
    length = agv.length
    serial_no = agv.serial_no
    agv_json = agv.to_json()
    agv_dict = json.loads(agv_json)
    assert agv_dict['length'] == length
    assert agv_dict['serial_no'] == serial_no


def test_json_to_agv_info():
    agv = create_agv(False)
    agv_json = agv.to_json()
    decoded_agv = agvi.json_to_agv_info(agv_json, for_calibration=False)
    assert agv == decoded_agv


def test_json_to_agv_info_for_calibration():
    agv = create_agv()
    agv_json = agv.to_json()
    decoded_agv = agvi.json_to_agv_info(agv_json)
    assert agv == decoded_agv
