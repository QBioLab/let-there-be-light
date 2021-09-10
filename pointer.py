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
        self.height_in_px = 0
        self.half_width_in_px = 370/2
        self.cage_width_in_mm = 200
        self.yaw_bias_in_degree = 0

    def set_pointer(self, x0, y0, half_width_in_px, height_in_mm, yaw_bias_in_degree):
        self.x0 = x0
        self.y0 = y0
        self.yaw_bias_in_degree =  yaw_bias_in_degree
        self.half_width_in_px = half_width_in_px
        self.height_in_px = height_in_mm / self.cage_width_in_mm * self.half_width_in_px * 2

    def point2mouse(self, centroid_x, centroid_y):
        """雲臺指向"""
        # calculate mouse position respect to gimbal
        #   -> y  /|\ x
        mouse_x = centroid_x - self.half_width_in_px + self.x0
        mouse_y = centroid_y - self.half_width_in_px + self.y0
        gimbal_pitch = self._xy2pitch_angle(mouse_x, mouse_y) 
        gimbal_yaw = self._xy2yaw_angle(mouse_x, mouse_y)
        print("pitch, yaw:", gimbal_pitch, gimbal_yaw)
        self.rotate_gimbal(gimbal_pitch, gimbal_yaw)

    def _xy2pitch_angle(self, x, y):
        # gimbal at horizon is 0 degree, then pitch axis walk in 90+-50 degree
        max_angle = 140
        min_angle = 40
        park_angle = 70
        dead_angle = 90
        dead_angle_offset = 0.1 
        # 取余角
        pitch_angle = 90 - np.arctan2(np.sign(x)*np.sqrt(x**2 + y**2), self.height_in_px)/np.pi*180
        if pitch_angle > max_angle or pitch_angle < min_angle :
            pitch_angle  = central_angle
        if pitch_angle == dead_angle:
            pitch_angle = pitch_angle + dead_angle_offset
        return pitch_angle

    def _xy2yaw_angle(self, x, y):
        # yaw axis walk in 0-180 degree
        max_angle = 100 
        min_angle = -100
        yaw_angle = np.sign(x)*np.arctan2(y, np.abs(x)) / np.pi*180 
        yaw_angle = yaw_angle + self.yaw_bias_in_degree
        if yaw_angle > max_angle :
            yaw_angle = max_angle
        if  yaw_angle < min_angle:
            yaw = min_angle
        return yaw_angle

    def cali_pointer(self, cam):
        """auto calibrate gimbal position"""
        print("calibrating gimbal in box")
