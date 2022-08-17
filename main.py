import cv2
from cv2 import threshold
from cv2 import THRESH_BINARY
import numpy as np
import defaults

from flask import Flask, render_template
from flask.wrappers import Response

import detect
from calibration.camera_calibration import calibrate_camera, undistort, is_calibrated
from alignment.alignment import align
from positioning import assess_position_abs_distances

from defaults import TOLERANCE, CAMERA_NUMBER, MARKER_TYPE, PARAMS_DIR, ALIGNMENT_TEMPLATE_IMG_PATH, STD_WAIT
from calibration import agv_pattern, agv_info
from segment import _threshold_img, cluster_dbscan, _threshold_img_adaptive, _code_contours, draw_contours, image_segments, masked_img #TODO remove protected method

from exceptions import InvalidBarcodeException, TooFewPointsException

app = Flask(__name__)

video = cv2.VideoCapture(CAMERA_NUMBER)

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

REQUIRED_POSITION = np.array([[141,  12], [769,  32], [746, 416], [133, 416]])


@app.route('/calibrate')
def calibrate():
    calibrate_camera(with_video=True)
    return 'Successfully calibrated'

def main():

    cap = cv2.VideoCapture(CAMERA_NUMBER)
    marker_type = MARKER_TYPE

    force_recalibration = False
    camera_calibrated = is_calibrated()

    if not camera_calibrated or force_recalibration:
        #calibrate_camera(with_video=True)
        print('Calibration sucessful')

    cal_mtx = np.load(f'{PARAMS_DIR}/calibration_matrix.npy')
    dist_mtx = np.load(f'{PARAMS_DIR}/distortion_coefficients.npy')

    template_image = cv2.imread(ALIGNMENT_TEMPLATE_IMG_PATH)

    while True:
        success, img = cap.read()

        if not success:
            raise RuntimeError('Image capture unsuccessful')


        threshold_img = _threshold_img_adaptive(img)
        #undistorted_img = undistort(img, cal_mtx, dist_mtx, alpha=0)

        try: 
            data, found = detect.find_markers(img, marker_type='aztec')  # boxes and IDs of found markers
        except InvalidBarcodeException:
            found = []
            data = 'Invalid code'


        try:
            distances = assess_position_abs_distances(img, REQUIRED_POSITION)
        except TooFewPointsException:
            distances = np.ones((4))*999
        except ValueError:
            distances = np.ones((4))*999
            cv2.imwrite('error_causing.jpg', img)
        # aligned_img = align(img, template_image , found, template_points)

        # cv2.resize(img, (undistorted_img.shape[0], undistorted_img.shape[1]), dst=img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        segment_big = np.zeros(gray.shape)
        
        try:
            seg_1 = image_segments(gray)[0]
            segment_big[0:seg_1.shape[0], 0:seg_1.shape[1]] = seg_1
            
        except IndexError:
            seg_1 = segment_big

        #draw_contours(img, _code_contours(img)[0])
        position_box_color = (0, 0, 255)  # TODO
        cv2.polylines(img, [REQUIRED_POSITION], isClosed=True, color=position_box_color)
        cv2.putText(img, f'Decoded: {data}', org=(100, 600), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(0, 255, 0))

        img_concat = np.concatenate((img, masked_img(img)), axis=0)
        cv2.imshow('Aligned', img_concat)
        print(data, found)
        print(distances)

        if cv2.waitKey(STD_WAIT) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()




if __name__ == '__main__':
    app.run()
