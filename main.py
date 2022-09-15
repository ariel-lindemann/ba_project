from collections import OrderedDict
import cv2
import numpy as np
import json
from calibration.agv_info import AgvInfo
import calibration.camera_calibration as camera_calibration
from defaults import CAMERA_NUMBER
import positioning.positioning as pos

from fastapi import FastAPI, HTTPException
from json import JSONEncoder

CURRENT_POSITION_MESSAGE = 'Current position'
LAST_POSITION_MESSAGE = 'Last detected position. WARNING: the AGV might be somewhere else'

required_position = np.array([[140,  10], [768,  30], [745, 414], [132, 414]])
current_position = np.array([[141,  12], [769,  32], [746, 416], [133, 416]])

agv_pool = OrderedDict({0: AgvInfo(560, 380, 200, 50, 50, 'default_agv')})

camera = CAMERA_NUMBER
cap = cv2.VideoCapture(camera)

app = FastAPI(title='AGV Positioning')


@app.on_event('startup')
async def main():
    print('Welcome')
    if not camera_calibration.is_calibrated():
        return{'message': 'camera is being calibrated'}
    return {'message': 'Welcome to AGV Positioning.'}

@app.get('/')
def welcome():
    return {'message': 'Welcome to AGV Positioning'}

@app.get('/distances/')
def get_discances():
    position_msg = get_position()
    current = position_msg['is_current']  # TODO
    position = ndarray_from_json(position_msg['position'])
    length = position_msg['agv_length']
    global required_position
    x_dist, y_dist, _ = pos.calculate_distances_in_mm(position, required_position, length) #TODO

    x_dist = ndarray_to_json(x_dist)
    y_dist = ndarray_to_json(y_dist)

    return {'message':'distances', 'is_current':current, 'x-distances': x_dist, 'y-distances': y_dist}


@app.get('/position/')
def get_position():
    success, img = cap.read()
    if not success:
        raise HTTPException(
            status_code=500, detail='image could not be captured')

    data, detected_position = pos.find_codes(img)
    current = True
    message = CURRENT_POSITION_MESSAGE
    if detected_position == []:
        current = False
        message = LAST_POSITION_MESSAGE
        length = get_last_agv().length
        data = [get_last_agv()]
    else :
        length = json.loads(data[0])['length']
        detected_position = np.array(detected_position)
        global current_position
        current_position = detected_position


    current_position = pos.get_transformed_points(current_position, data[0])

    return {'message': message, 'is_current': current, 'position': ndarray_to_json(current_position), 'agv_length':length}


@app.get('/position/last')
def get_last_position():
    return {'message': LAST_POSITION_MESSAGE, 'is_current': False, 'position': ndarray_to_json(current_position)}


@app.put('/position/set_as_target/')
def set_current_as_required():
    global required_position
    required_position = current_position
    return {'message': 'new target set successfully'}


@app.get('/target/')
def get_target():
    return ndarray_to_json(required_position)


@app.get('/calibrate_camera/')
def calibrate_camera():
    camera_calibration.calibrate_camera(with_video=False)
    return {'message': 'camera calibrated'}


@app.get('/calibrate_camera/manual/')
def calibrate_camera_manually():
    camera_calibration.calibrate_camera(with_video=True)


@app.get('/calibrate_camera/check_calibration_status/')
def check_calibration_status():
    result = camera_calibration.is_calibrated()
    specifier = ''
    if not result:
        specifier = ' not '
    return {'message': f'Camera is{specifier} calibrated', 'calibration_status': result}


@app.get('/agv_info/')
def get_agv_pool():
    '''
    returns all AGVs
    '''
    global agv_pool
    return agv_pool


@app.post('/agv_info/{id}/')
def create_agv_info(id: int, length=560, width=380, height=200, raster_x=50, raster_y=50, serial_no='default_agv'):
    '''
    create an AGV at the specified index

    example /agv_info/3/?length=560/?length=570&width?380&height=200&serial_no=example
    '''
    agv = AgvInfo(length, width, height, raster_x, raster_y, serial_no)
    global agv_pool
    agv_pool.update({id: agv})


@app.put('/agv_info/{id}/')
def change_agv_info(id: int, length=560, width=380, height=200, raster_x=50, raster_y=50, serial_no='default_agv'):
    '''
    update the AGV at the specified index position

    example /agv_info/3/?length=560/?length=570&width?380&height=200&serial_no=example
    '''
    agv = AgvInfo(length, width, height, raster_x, raster_y, serial_no)
    global agv_pool
    agv_pool.update({id: agv})


@app.get('/agv_info/{id}/')
def get_agv_info(id: int):
    '''
    get an AGV from the pool at the specified index
    '''
    return agv_pool[id]


@app.delete('/agv_info/{id}/')
def delete_agv_info(id: int):
    '''
    delete an AGV from the pool
    '''
    del agv_pool[id]


@app.put('/camera/{camera_no}/')
def change_camera(camera_no: int):
    '''
    change the camera if you have more than one (default value is 0)
    '''
    global camera
    camera = camera_no
    return{'message': 'now using camera {camera_no}'}


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def ndarray_to_json(n):
    encoded = json.dumps(n, cls=NumpyArrayEncoder)
    return encoded


def ndarray_from_json(j):
    decoded = json.loads(j)
    return np.asarray(decoded)

def get_last_agv():
    global agv_pool
    last_agv = list(agv_pool.values())[-1]
    return last_agv