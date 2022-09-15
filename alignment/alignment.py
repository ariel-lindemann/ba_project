import cv2
import numpy as np

def align(img, template,  img_points,  template_points):
    img_points = np.transpose(img_points)
    template_points = np.transpose(template_points)

    pairs = find_pairs(img_points, template_points)

    template_points = pairs[:][0]
    img_points = pairs[:][1]

    homography = cv2.findHomography(template_points, img_points)

    template_height, template_width, channels = template.shape
    aligned = cv2.warpPerspective(img, homography, (template_height, template_width))

    return aligned

def find_pairs(img_points, template_points):
    pairs = np.array([])

    if not img_points.any() : return pairs

    # find corresponding pairs between image and template
    for img_point in img_points:
        marker_id = img_point[1]
        for t_point in template_points:
            if t_point[1]==marker_id:
                pairs = np.concatenate(pairs, np.array([img_point[0], t_point[0]]))
                np.delete(template_points, [t_point])
                break 

    return pairs