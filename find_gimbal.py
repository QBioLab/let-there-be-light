import sys
import json
import time
import cv2 as cv
import numpy as np
import libgimbal

with open(sys.argv[1], 'r') as config_file:
    config = json.load(config_file)
cage_id = config['cage_id']
cam = cv.VideoCapture(config['cam_idx'])
gimbal = libgimbal.gimbal(config['gimbal_path'])
gimbal.park_gimbal()
count = 0

# dry run for camera to set up
while cam.isOpened() and count < 30:
    ret, frame = cam.read()
    if ret :
        count = count + 1

_, full_view_image = cam.read()
print("capturing full view image")
cv.imwrite("cali/cage_%d_full.png"%cage_id, full_view_image)
print("capture full view image don")

# rotate and capture 
pitch_down_angle = 90
yaw_rotate_seq = [0, 90, 180, -90]
print("capturing gimbal center image")
for yaw_angle in yaw_rotate_seq:
    gimbal.rotate_gimbal(pitch_down_angle, yaw_angle)
    print(yaw_angle, end=" ")
    time.sleep(1)
    ret, frame = cam.read()
    if ret:
        cropped_frame = frame[config['roi_y0']:config['roi_y1'], \
                config['roi_x0']:config['roi_x1']]
        #cv.imshow('test', cropped_frame)
        cv.imwrite("cali/cage_%d_center_%d.png"%(cage_id, yaw_angle), cropped_frame)

print("capture gimbal center image done")
time.sleep(2)
gimbal.park_gimbal()
cv.destroyAllWindows()
cam.release()

