from exceptions import TooFewPointsException


import cv2
import numpy as np

def draw_result(img, p):
    bl = (p.bottom_left.x, p.bottom_left.y)
    tl = (p.top_left.x, p.top_left.y)
    tr = (p.top_right.x, p.top_right.y)
    br = (p.bottom_right.x, p.bottom_right.y)

    cv2.polylines(img, np.array([[tl, bl, br, tr]]), isClosed=True, color=(255, 000, 000))

def draw_distance_lines(img, points1, points2):
    if len(points1) != len(points2):
        raise TooFewPointsException
    
    lines_img = img.copy()

    for i in range(4):
        #TODO adaptive color
        cv2.line(lines_img, pt1=points1[i], pt2=points2[i], color=(0,255,0))

    return lines_img

def draw_points(img, points, font_size=10):
    for i in range(points.shape[0]):
        x = points[i][0].astype(np.int32)
        y = points[i][1].astype(np.int32)
        cv2.putText(img, str(i), (x,y), cv2.FONT_HERSHEY_PLAIN, font_size, color=(0, 0, 255), thickness=5)
        cv2.circle(img, (x,y), 5, (0, 255, 0), 10)
    return img