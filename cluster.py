import cv2
import numpy as np

from sklearn.cluster import DBSCAN

#TODO 1 find the clusters
# DBSCAN what are we looking for?
# black points from the thresholded image
#TODO 2 filter those who are not codes (squares)
#TODO 3 find the box of the cluster
#TODO 4 segment the image accordingly


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

def cluster_dbscan(img, eps = 0.4, min_samples = 20):
    Z = np.float32(img.reshape((-1,3)))
    db = DBSCAN(eps= eps, min_samples=min_samples).fit(Z[:,:2])
    return np.uint8(db.labels_.reshape(img.shape[:2]))
    #TODO