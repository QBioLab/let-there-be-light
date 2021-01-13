#!/bin/python3

from gpiozero import AngularServo
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import numpy as np

pitch = AngularServo(13)
yaw = AngularServo(12)
m = PyMouse()
#k = PyKeyboard()
filed = m.screen_size()
h = 25*filed[1]/22 # height's pixel number

while(input() == 'q'):
    x = m.position()[1] - filed[1]/2
    y = m.position()[2] - filed[2]/2
    alpha = np.arctan(x/h) 
    beta = np.arctan(y/x)
    pitch.angle = alpha
    yaw.angle = beta
