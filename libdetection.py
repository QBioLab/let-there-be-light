import cv2 as cv
import numpy as np

"""
detecte mouse and laser point
"""

def detecte_laser(frame):
    blue_mask = cv.inRange(frame, (0, 0, 220), (255, 255, 255)) 
    if np.all(blue_mask == 0):
        print("blue mask is empty")
        return None
    morphology_blue = cv.erode(blue_mask, cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5)))
    if np.all(morphology_blue == 0):
        print("morphology blue is empty")
        return None
    contour_blue, hierarchy_blue = cv.findContours(morphology_blue, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
    if len(contour_blue) == 0:
        print('contour_blue is empty')
        return None
    moment_blue = cv.moments(contour_blue[-1])
    if moment_blue['m00'] == 0:
        print('contour_blue = Open', count)
        return None
    centroid_blue_x = round(moment_blue['m10'] / moment_blue['m00'])
    centroid_blue_y = round(moment_blue['m01'] / moment_blue['m00'])
    #centroid_blue_result = cv.circle(procession, (centroid_blue_x, centroid_blue_y), 5, (0, 255, 0), -1)
    return centroid_blue_x, centroid_blue_y

def detecte_mouse(frame):
    return None
