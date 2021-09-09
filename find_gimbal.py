import sys
import json
import time
import cv2 as cv
import numpy as np
import libgimbal

with open(sys.argv[1], 'r') as config_file:
    config = json.load(config_file)
cam = cv.VideoCapture(config['cam_idx'])
gimbal = libgimbal.gimbal(config['gimbal_path'])
gimbal.park_gimbal()
count = 0

# dry run for camera to set up
while cam.isOpened() and count < 30:
    ret, frame = cam.read()
    if ret :
        count = count + 1
# rotate and capture 
yaw_rotate_seq = [0, 90, 180, -90]
for yaw_angle in yaw_rotate_seq:
    gimbal.rotate_gimbal(90, yaw_angle)
    time.sleep(1)
    ret, frame = cam.read()
    cv.imshow('test', frame)
    cv.imwrite("90-%d.tiff"%yaw_angle, frame)

cv.destroyAllWindows()
cam.release()

