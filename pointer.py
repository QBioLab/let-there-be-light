#!/bin/python3
import numpy as np
from libgimbal import gimbal

class Pointer(gimbal):
    def __init__(self, PORT):
        super().__init__(PORT)
        self.park_gimbal()
        #云台中心的笼底投影
        self.x0 = 0
        self.y0 = 0
        self.height = 0
        self.half_width = 370/2
        self.yaw_bias = 0

    def set_pointer(self, x0, y0, half_width, mm_height, yaw_bias):
        self.x0 = x0
        self.y0 = y0
        self.yaw_bias =  yaw_bias
        self.half_width = half_width
        self.height = mm_height / 200 * self.half_width * 2

    def point2mouse(self, centroid_x, centroid_y):
        """雲臺指向"""
        gimbal_x = centroid_x - self.half_width + self.x0
        gimbal_y = centroid_y - self.half_width + self.y0
        gimbal_pitch = 4096 - int(np.arctan2(np.sqrt(gimbal_x**2 + gimbal_y**2), self.height) / np.pi * 8192)
        gimbal_yaw = int(np.arctan2(gimbal_y, gimbal_x) / np.pi * 8192) + self.yaw_bias
        print("pitch, yaw:", gimbal_pitch, gimbal_yaw)
        self.rotate_gimbal(gimbal_pitch, gimbal_yaw)
    
    def cali_pointer(self, cam):
        """auto calibrate gimbal position"""
        print("calibrating gimbal in box")
