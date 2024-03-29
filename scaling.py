import cv2


def scale_to_size(img, desired=1000):
    scale = scale_parameter(img, desired=desired)
    img = _downscale_image(img, scale)
    return img, scale


def scale_parameter(img, desired=1000):
    height = img.shape[0]
    width = img.shape[1]

    if height > width:
        scale = height//desired + 1
    else:
        scale = width//desired + 1

    return scale


def _downscale_image(img, scale: int):
    return cv2.resize(img, (img.shape[1]//scale, img.shape[0]//scale))
