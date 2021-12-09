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
cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
gimbal = libgimbal.gimbal(config['gimbal_path'])
gimbal.park_gimbal()
count = 0

# rotate and capture 
pitch_down_angle = 90
yaw_rotate_seq = [0, 90, 180, -90]
print("capturing gimbal center image")
for yaw_angle in yaw_rotate_seq:
    gimbal.rotate_gimbal(pitch_down_angle, yaw_angle)
    print(yaw_angle, end=" ")
    time.sleep(2)
    ret, frame = cam.read()
    if ret:
        cv.imwrite("cali/20211208-cage_%d_center_%d.png"%(cage_id, yaw_angle), frame)

print("capture gimbal center image done")
time.sleep(2)
gimbal.park_gimbal()
cam.release()

