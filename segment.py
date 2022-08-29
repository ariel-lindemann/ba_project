import cv2
from cv2 import contourArea
import numpy as np

from sklearn.cluster import DBSCAN

THRESHOLD_BLOCK_SIZE = 51
THRESHOLD_CONSTANT = 5

#TODO dynamic size (based on code type)
MIN_SEGMENT_AREA = 2500

def _threshold_img_adaptive(img, blur=101):
    canny_img = cv2.Canny(img, 150, 200)
    canny_blurred = cv2.GaussianBlur(canny_img, (blur, blur), 0)
    threshold_img = cv2.adaptiveThreshold(canny_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, THRESHOLD_BLOCK_SIZE, THRESHOLD_CONSTANT)
    #threshold_img = cv2.cvtColor(threshold_img, cv2.COLOR_GRAY2BGR)
    return threshold_img

def _threshold_img(img, blur = 101):
    thr1 = 150
    thr2 = 200
    canny_img = cv2.Canny(img, thr1, thr2)
    canny_blurred = cv2.GaussianBlur(canny_img, (blur, blur), 0)
    mask = cv2.threshold(canny_blurred, 50, 255, cv2.THRESH_BINARY)[1]

    return mask


def cluster_dbscan(img, eps = 0.4, min_samples = 20):
    img = _threshold_img_adaptive(img)
    Z = np.float32(img.reshape((-1,3)))
    db = DBSCAN(eps= eps, min_samples=min_samples).fit(Z[:,:2])
    return np.uint8(db.labels_.reshape(img.shape[:2]))
    #TODO


def _code_contours(img, min_area=MIN_SEGMENT_AREA):
    '''
    returns the contours of areas where codes could be
    '''
    #TODO flexible parameters
    #TODO minimum size
    mask = _threshold_img(img)
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = _filter_by_min_area(contours, min_area)

    return contours


def _filter_by_min_area(contours, min_area):
    # filter out the ones which are too small
    new_cnts = []
    for c in contours:
        area = cv2.contourArea(c)
        if area >= min_area:
            new_cnts.append(c)

    return new_cnts


def draw_contours(img, cnts):

    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ((c_x, c_y), radius) = cv2.minEnclosingCircle(c)
        #cv2.circle(img, (int(c_x), int(c_y)), int(radius), (0, 0, 255), 3)
        cv2.rectangle(img, (x, y), ((x+w), (y+h)), (0,255,0), 3)
        cv2.putText(img, "#{}".format(i + 1), (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)


def masked_img(img):
    thr1=150 
    thr2=200
    canny_img = cv2.Canny(img, thr1, thr2)
    canny_blurred = cv2.GaussianBlur(canny_img, (101, 101), 0)
    thresh = cv2.threshold(canny_blurred, 50, 255, cv2.THRESH_BINARY)[1]

    masked_img = cv2.bitwise_and(img, img, mask=thresh)
    return masked_img
    

def _image_segments_by_contours(img, cnts, padding=25):
    imgs = []
    #TODO dynamic padding

    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        segment = img[(y-padding):(y+w+padding), (x-padding):(x+h+padding)]
        imgs.append(segment)

    return imgs


def image_segments(img):
    cnts = _code_contours(img)[0]
    segments = _image_segments_by_contours(img, cnts)
    return segments

# TODO replace with real positions of codes
def segment_positions(img):
    cnts = _code_contours(img)[0]
    points = np.zeros((len(cnts), 2))
    for (i, c) in enumerate(cnts):
        # compute the center from contour moments
        M = cv2.moments(c)
        try:
            x = int(M['m10'] / M['m00'])
            y = int(M['m01'] / M['m00'])
        except ZeroDivisionError:
            x, y = 0, 0

        points[i] = (x,y)

    return points
