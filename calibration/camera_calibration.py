import cv2
import numpy as np

import os
import glob

DATA_DIR = "data"
CALIBRATION_IMGS_PATH = f'{DATA_DIR}/calibration_images'
CALIBRATION_RES = f'{DATA_DIR}/calibration_results'
PARAMS_DIR = f'{DATA_DIR}/camera_parameters'


def calibrate_camera(imgs_path=CALIBRATION_IMGS_PATH):
    """
    Calibrate camera using images in the given path
    """

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    images = glob.glob(f'{imgs_path}/*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)
        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (9, 6), corners2, ret)
            new_name = fname.split('/')[1]
            cv2.imwrite(f'{CALIBRATION_RES}/{new_name}', img)
    cv2.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    np.save(f'{PARAMS_DIR}/calibration_matrix', mtx)
    np.save(f'{PARAMS_DIR}/distortion_coefficients', dist)

    np.save(f'{PARAMS_DIR}/rotation_vectors', rvecs)
    np.save(f'{PARAMS_DIR}/translation_vectors', tvecs)

    return ret, mtx, dist, rvecs, tvecs


def undistort(img, cal_mtx, dist, alpha=1.0):
    """Reverse distortion based on intrinsic parameters

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
    """

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
    print("total error: {}".format(mean_error/len(objpoints)))


# TODO check for names
def is_calibrated():
    '''Checks if the camera is calibrated (if camera parameters are present)'''
    params_dir = os.listdir(PARAMS_DIR)
    if len(params_dir) == 0:
        return False
    else:
        return True
