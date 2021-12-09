#!/bin/python3
import numpy as np
from libgimbal import gimbal

class Pointer(gimbal):
    def __init__(self, PORT):
        super().__init__(PORT)
        self.park_gimbal()
        #云台中心的笼底投影
        self.gimbal_x0 = 0
        self.gimbal_y0 = 0
        self.height_in_px = 0
        self.half_width_in_px = 370/2
        self.cage_width_in_mm = 200
        self.yaw_bias_in_degree = 0

    def set_pointer(self, x0, y0, half_width_in_px, height_in_mm, yaw_bias_in_degree):
        self.gimbal_x0 = x0
        self.gimbal_y0 = y0
        self.yaw_bias_in_degree =  yaw_bias_in_degree
        self.half_width_in_px = half_width_in_px
        self.height_in_px = height_in_mm / self.cage_width_in_mm * self.half_width_in_px * 2

    def point2mouse(self, mouse_x_ref2cam, mouse_y_ref2cam):
        """雲臺指向"""
        # convert mouse position refer from camera to gimbal
        #   -> y  /|\ x
        print(mouse_x_ref2cam, mouse_y_ref2cam)
        #mouse_x_ref2gim = mouse_x_ref2cam + self.gimbal_x0  - self.half_width_in_px
        #mouse_y_ref2gim = mouse_y_ref2cam + self.gimbal_y0  - self.half_width_in_px
        mouse_x_ref2gim = mouse_x_ref2cam - self.gimbal_x0  
        mouse_y_ref2gim = mouse_y_ref2cam - self.gimbal_y0 
        # convert Cartesian coordinate to Polar coordinate
        gimbal_pitch = self._xy2pitch_angle(mouse_x_ref2gim, mouse_y_ref2gim) 
        gimbal_yaw = self._xy2yaw_angle(mouse_x_ref2gim, mouse_y_ref2gim)
        print("x, y:", mouse_x_ref2gim, mouse_x_ref2gim)
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
        pitch_angle = 90 - np.arctan(np.sign(-x)*np.sqrt(x**2 + y**2)/self.height_in_px)/np.pi*180
        if pitch_angle > max_angle or pitch_angle < min_angle :
            pitch_angle = park_angle
        if pitch_angle == dead_angle:
            pitch_angle = pitch_angle + dead_angle_offset
        return pitch_angle

    def _xy2yaw_angle(self, x, y):
        # yaw axis walk from -90 to +90 degree
        max_angle = 100 
        min_angle = -100
        if not x == 0: # avoid to divide 0
            x = x + 0.00001
        yaw_angle = np.arctan(y/x) / np.pi*180 
        yaw_angle = yaw_angle + self.yaw_bias_in_degree
        if yaw_angle > max_angle :
            yaw_angle = max_angle
        if  yaw_angle < min_angle:
            yaw = min_angle
        return yaw_angle

    def cali_pointer(self, cam):
        """auto calibrate gimbal position"""
        print("calibrating gimbal in box")
