import threading
import cv2
from cv2 import threshold
from cv2 import THRESH_BINARY
import numpy as np

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import visualisation as viz
from calibration.camera_calibration import calibrate_camera, undistort, is_calibrated
from positioning.positioning import calculate_distances_in_mm, get_data_and_position_points

from defaults import  CAMERA_NUMBER, PARAMS_DIR, ALIGNMENT_TEMPLATE_IMG_PATH, STD_WAIT
from calibration import agv_pattern, agv_info

from exceptions import InvalidBarcodeException, TooFewPointsException

app = FastAPI()
lock = threading.Lock()

video = cv2.VideoCapture(CAMERA_NUMBER)
current_position = None
distances = np.zeros(4)
output_frame = None #TODO

REQUIRED_POSITION = np.array([[141,  12], [769,  32], [746, 416], [133, 416]])

def gen(video):
    while True:
        success, image = video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def generate():
    global output_frame, lock
    while True:
        # wait until lock is acquired
        with lock:
            if output_frame is None:
                continue
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield b''+bytearray(encoded_image)

               
@app.get('/video_feed')
def video_endpoint():
    global video
    return StreamingResponse(generate())

@app.get('/distances')
def get_distances():
    return {0:distances[0], 1:distances[1], 2:distances[2], 3:distances[3]}

@app.get('/frame')
def get_current_frame():
    global output_frame
    return output_frame
    
def create_templates():
    agv = agv_info.AgvInfo(560, 380, 200, 50, 50, 'test')
    pattern_size = 100
    img_format = 'jpg'
    codes=['qr', 'datamatrix', 'aztec']
    for c in codes:
        print(f'creating {c} ...')
        agv_pattern.create_agv_template(agv, pattern_size, c, border=500, img_path=f'evaluation_pattern/{c}_big.{img_format}') 
        agv_pattern.create_agv_template(agv, pattern_size//2, c, border=500, img_path=f'evaluation_pattern/{c}_small.{img_format}') 


def main():

    cap = cv2.VideoCapture(CAMERA_NUMBER)

    force_recalibration = False
    camera_calibrated = is_calibrated()

    required_position = np.array([[141,  12], [769,  32], [746, 416], [133, 416]])

    if not camera_calibrated or force_recalibration:
        print('Calibrating camera ...')
        calibrate_camera(with_video=False)
        print('Calibration sucessful')

    cam_mtx = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    dist_vecs = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    while (cap.isOpened()):
        success, img = cap.read()
        old_img = img.copy()

        if not success:
            raise RuntimeError('Image capture unsuccessful')

        old_img = img.copy()
        img = undistort(img, cam_mtx, dist_vecs, alpha=0)

        try: 
            data, positions = get_data_and_position_points(img)# text and position of found codes
        except InvalidBarcodeException:
            positions = []
            data = 'Invalid code'


        global distances
        global output_frame
        
        try:
            distances = calculate_distances_in_mm(positions, required_position, data[0].length)
        except (TooFewPointsException, IndexError):
            distances = np.ones((4))*999
        except ValueError:
            distances = np.ones((4))*999
            cv2.imwrite('data/error_causing_images/value_error_when_assessing_distance.jpg', img)


        position_box_color = (0, 0, 255)
        cv2.polylines(img, [required_position], isClosed=True, color=position_box_color)
        viz.draw_points(img, np.array(positions))
            
        cv2.putText(img, f'Decoded: {len(data)} codes', org=(100, 600), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(0, 255, 0))

        cv2.imshow('AGV Positioning', img)
        print(data, positions)
        print(distances)

        pressed_key = cv2.waitKey(STD_WAIT) & 0xFF

        if pressed_key == ord('s'):
            cv2.imwrite('saved.jpg', old_img)
        elif pressed_key == ord('h'):
            required_position = current_position
        elif pressed_key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
