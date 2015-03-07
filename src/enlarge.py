import numpy as np
import cv2

def enlargeimage(img, scale,
            path=False):
    if path is True:
        img = cv2.imread(img,0)

    height,width = img.shape[:2]
    beginH = int(round(height*scale))
    endH = int(round(height-beginH))
    beginW = int(round(width*scale))
    endW = int(round(width-beginW))
    spliced_img = np.zeros((abs(endH-beginH),abs(endW-beginW)), np.uint8)
    if beginH < endH and beginW < endW:
        spliced_img[:] = img[beginH:endH,beginW:endW]
    else:
        spliced_img[:] = img[endH:beginH,endW:beginW]
    return spliced_img

