#!/bin/python3

from gpiozero import AngularServo
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import numpy as np
import time 

pitch = AngularServo(12)
yaw = AngularServo(13)
m = PyMouse()
#k = PyKeyboard()
filed = m.screen_size()
h = 25*filed[0]/22 # height's pixel number

#while(input() = 'q'):
while(True):
    time.sleep(0.001) 
    pos = m.position()
    x = pos[0] - filed[0]/2
    y = pos[1] - filed[1]/2
    alpha = np.arctan(x/h)*12*np.pi
    if x == 0:
       beta = 0 
    else:
        beta = np.arctan(y/x)*12*np.pi
    #print("1", flush=True)
    print(alpha, beta, flush=True)
    pitch.angle = alpha
    yaw.angle = beta
