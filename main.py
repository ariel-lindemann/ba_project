import json
import cv2
from cv2 import threshold
from cv2 import THRESH_BINARY
import numpy as np
import defaults

from flask import Flask, render_template
from flask.wrappers import Response

import detect
import visualisation as viz
from calibration.camera_calibration import calibrate_camera, undistort, is_calibrated
from alignment.alignment import align
from positioning.positioning import calculate_abs_distances_in_mm, get_data_and_position_points, pos_to_dict

from defaults import CALIBRATION_RESULTS_PATH, TOLERANCE, CAMERA_NUMBER, MARKER_TYPE, PARAMS_DIR, ALIGNMENT_TEMPLATE_IMG_PATH, STD_WAIT
from calibration import agv_pattern, agv_info
from segment import _threshold_img_adaptive, image_segments, masked_img #TODO remove protected method

from exceptions import InvalidBarcodeException, TooFewPointsException

app = Flask(__name__)

video = cv2.VideoCapture(CAMERA_NUMBER)
position = None
distances = None

REQUIRED_POSITION = np.array([[141,  12], [769,  32], [746, 416], [133, 416]])

@app.route('/')
def index():
    return render_template('index.html')
    
def gen(video):
    while True:
        success, image = video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
               
@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/posiotion')
def latest_position():
    if position:
        return pos_to_dict(position)
    else:
        return Response('Position could not be established', 500) #TODO should it be 404?


@app.route('/distances')
def latest_distances():
    if distances:
        return pos_to_dict(distances)
    else:
        return Response('Distances could not be measured', 500) #TODO should it be 404?


@app.route('/calibrate')
def calibrate():
    calibrate_camera(with_video=True)
    return 'Successfully calibrated'

@app.route('/set_current_pos_as_required')
def set_current_pos_as_required():
    #TODO
    pass

def main():

    cap = cv2.VideoCapture(CAMERA_NUMBER)

    force_recalibration = False
    camera_calibrated = is_calibrated()

    if not camera_calibrated or force_recalibration:
        print('Calibrating camera ...')
        calibrate_camera(with_video=False)
        print('Calibration sucessful')

    cam_mtx = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    dist_vecs = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    template_image = cv2.imread(ALIGNMENT_TEMPLATE_IMG_PATH)


    while (cap.isOpened()):
        success, img = cap.read()
        old_img = img.copy()

        if not success:
            raise RuntimeError('Image capture unsuccessful')

        #undistorted_img = undistort(img, cal_mtx, dist_mtx, alpha=0)

        try: 
            data, positions = get_data_and_position_points(img)# text and position of found codes
        except InvalidBarcodeException:
            positions = []
            data = 'Invalid code'


        #TODO aviod calculating points twice (maybe change discances function to accept points)
        try:
            distances = calculate_abs_distances_in_mm(positions, REQUIRED_POSITION, data[0])
        except (TooFewPointsException, IndexError):
            distances = np.ones((4))*999
        except ValueError:
            distances = np.ones((4))*999
            cv2.imwrite('data/error_causing_images/value_error_when_assessing_distance.jpg', img)

        # cv2.resize(img, (undistorted_img.shape[0], undistorted_img.shape[1]), dst=img)

        position_box_color = (0, 0, 255)  # TODO
        cv2.polylines(img, [REQUIRED_POSITION], isClosed=True, color=position_box_color)
        viz.draw_points(img, np.array(positions)) #TODO find alternative (deprecated)
            
        cv2.putText(img, f'Decoded: {len(data)} codes', org=(100, 600), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(0, 255, 0))

        img_concat = np.concatenate((img, masked_img(img)), axis=0)
        cv2.imshow('Aligned', img_concat)
        print(data, positions)
        print(distances)

        pressed_key = cv2.waitKey(STD_WAIT) & 0xFF

        if pressed_key == ord('s'):
            cv2.imwrite('saved.jpg', old_img)
        elif pressed_key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
    #app.run()
    main()
