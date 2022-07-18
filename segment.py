import cv2
import numpy as np

from sklearn.cluster import DBSCAN


#TODO 1 find the clusters
# DBSCAN what are we looking for?
# black points from the thresholded image
#TODO 2 filter those who are not codes (squares)
#TODO 3 find the box of the cluster
#TODO 4 segment the image accordingly

THRESHOLD_BLOCK_SIZE = 21
THRESHOLD_CONSTANT = 5

def k_means_cluster(img, k):
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # convert to RGB
    pixels = img.reshape(-1,3) # reshape to 2D array
    pixels = np.float32(pixels)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.2)

    ret, label, center = cv2.kmeans(pixels, k, 10, criteria, 0, cv2.KMEANS_PP_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape(img.shape)

    return res2, center


def img_points_with_colors(img, color_value):
    img_points = []

    return 0

def _threshold_img(img):
    canny_img = cv2.Canny(img, 150, 200)
    threshold_img = cv2.adaptiveThreshold(canny_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, THRESHOLD_BLOCK_SIZE, THRESHOLD_CONSTANT)
    threshold_img = cv2.cvtColor(threshold_img, cv2.COLOR_GRAY2BGR)
    return threshold_img

def cluster_dbscan(img, eps = 0.4, min_samples = 20):
    img = _threshold_img(img)
    Z = np.float32(img.reshape((-1,3)))
    db = DBSCAN(eps= eps, min_samples=min_samples).fit(Z[:,:2])
    return np.uint8(db.labels_.reshape(img.shape[:2]))
    #TODO


def code_masks(img, thr1=150, thr2=200):
    '''
    returns the masks of areas where codes could be
    '''
    #TODO flexible parameters
    canny_img = cv2.Canny(img, thr1, thr2)
    canny_blurred = cv2.GaussianBlur(canny_img, (101, 101), 0)
    mask = cv2.threshold(canny_blurred, 50, 255, cv2.THRESH_BINARY)[1]

    #TODO return masks
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return cnts


def draw_contours(img, cnts):

    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ((c_x, c_y), radius) = cv2.minEnclosingCircle(c)
        cv2.circle(img, (int(c_x), int(c_y)), int(radius), (0, 0, 255), 3)
        cv2.putText(img, "#{}".format(i + 1), (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)


def image_segments(img, cnts):
    imgs = []

    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        segment = img[x:y, w:h]
        imgs.append(segment)

    return imgs


def masked_img(img):
    thr1=150 
    thr2=200
    canny_img = cv2.Canny(img, thr1, thr2)
    canny_blurred = cv2.GaussianBlur(canny_img, (101, 101), 0)
    thresh = cv2.threshold(canny_blurred, 50, 255, cv2.THRESH_BINARY)[1]

    masked_img = cv2.bitwise_and(img, img, mask=thresh)
    return masked_img