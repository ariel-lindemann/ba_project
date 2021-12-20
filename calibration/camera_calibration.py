import cv2
import numpy as np

import os
import glob

from defaults import CALIBRATION_IMGS_PATH, CALIBRATION_RESULTS_PATH, CAMERA_NUMBER, PARAMS_DIR, CALIBRATION_IMGS_FORMAT, CALIBRATION_CORNERS_X, CALIBRATION_CORNERS_Y


def calibrate_camera(with_video=True, imgs_path=CALIBRATION_IMGS_PATH, corners_x = CALIBRATION_CORNERS_X, corners_y = CALIBRATION_CORNERS_Y):
    '''
    Calibrate camera using images in the given path

    Parameters
    ------------

    with_video: bool
        if True, then the calibration images will be taken from the camera feed. 
        Otherwise they will be read from the calibraition images path

    imgs_path: String, optional
        where to look for calibration images (relative path). Only needed if `with_video` is False.
    '''

    CORNERS_X = corners_x
    CORNERS_Y = corners_y

    if with_video:
        produce_calibration_images()

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((CORNERS_Y*CORNERS_X, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CORNERS_X, 0:CORNERS_Y].T.reshape(-1, 2)
    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    images = glob.glob(f'{imgs_path}/*.{CALIBRATION_IMGS_FORMAT}')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (CORNERS_X, CORNERS_Y), None)
        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (CORNERS_X, CORNERS_Y), corners2, ret)
            n = fname.split('/')
            new_name = n[len(n) - 1]
            cv2.imwrite(f'{CALIBRATION_RESULTS_PATH}/{new_name}', img)
    cv2.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    np.save(f'{PARAMS_DIR}/calibration_matrix', mtx)
    np.save(f'{PARAMS_DIR}/distortion_coefficients', dist)

    np.save(f'{PARAMS_DIR}/rotation_vectors', rvecs)
    np.save(f'{PARAMS_DIR}/translation_vectors', tvecs)

    return ret, mtx, dist, rvecs, tvecs


def produce_calibration_images(amount=15, format=CALIBRATION_IMGS_FORMAT):
    '''
    Produces `amount` number of images from camera feed in the specified format and stores them in the calibration images directory.
    '''

    cap = cv2.VideoCapture(CAMERA_NUMBER)
    
    rate = 50
    time = rate * amount
    img_no = 0

    for i in range(time):

        success, img = cap.read()

        if not success:
            raise RuntimeError('Camera capture unsuccessful')

        img_with_text = img
        cv2.imshow('Calibration', img_with_text)

        # TODO better condition
        if i%rate == 0:
            cv2.imwrite(f'{CALIBRATION_IMGS_PATH}/cal_img_{img_no}.{format}', img)
            print(f'Calibrating... {amount - img_no} more to go')
            img_no += 1

# TODO fix
def undistort(img, cal_mtx, dist, alpha=1.0):
    '''
    Reverse distortion based on intrinsic parameters

    Parameters
    ----------
    img:
        the image to undistort

    cal_mtx:
        the calibration matrix

    dist:
        the distortion coefficients

    alpha:
        scaling parameter which determines how many pixels of the original image are retained. For alpha=0, some pixels
        may be removed, whereas for alpha=1 all original pixels are retained, while adding additional black pixels where
        required.
    '''

    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cal_mtx, dist, (w, h), alpha, (w, h))

    undistorted = cv2.undistort(img, cal_mtx, dist, None, newcameramtx)

    # image is cropped
    x, y, w, h = roi
    undistorted = undistorted[y:y+h, x:x+w]

    return undistorted


def calc_reprojection_err(objpoints, imgpoints, mtx, dist, rvecs, tvecs):
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error
    print('total error: {}'.format(mean_error/len(objpoints)))


# TODO check for names
def is_calibrated():
    '''Checks if the camera is calibrated (if camera parameters are present)'''
    params_dir = os.listdir(PARAMS_DIR)
    if len(params_dir) <= 1:
        return False
    else:
        return True
