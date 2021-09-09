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
        # calculate mouse position respect to gimbal
        #   -> y  /|\ x
        mouse_x = centroid_x - self.half_width + self.x0
        mouse_y = centroid_y - self.half_width + self.y0
        gimbal_pitch = self._xy2pitch_angle(mouse_x, mouse_y) 
        gimbal_yaw = self._xy2yaw_angle(mouse_x, mouse_y)
        print("pitch, yaw:", gimbal_pitch, gimbal_yaw)
        self.rotate_gimbal(gimbal_pitch, gimbal_yaw)

    def _xy2pitch_angle(self, x, y):
        # gimbal at horizon is 0 degree, then pitch axis walk in 90+-50 degree
        max_angle = 140
        min_angle = 40
        central_angle = 90
        # 取余角
        pitch_angle = 90 - np.arctan2(np.sign(x)*np.sqrt(x**2 + y**2), self.height)/np.pi*180
        if pitch_angle > max_angle or pitch_angle < min_angle :
            pitch_angle  = central_angle
        return pitch_angle

    def _xy2yaw_angle(self, x, y):
        # yaw axis walk in 0-180 degree
        max_angle = 100 
        min_angle = -100
        yaw_angle = np.sign(x)*np.arctan2(y, np.abs(x)) / np.pi*180 
        yaw_angle = yaw_angle + self.yaw_bias
        if yaw_angle > max_angle :
            yaw_angle = max_angle
        if  yaw_angle < min_angle:
            yaw = min_angle
        return yaw_angle

    def cali_pointer(self, cam):
        """auto calibrate gimbal position"""
        print("calibrating gimbal in box")
