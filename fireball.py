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
h = 15*filed[0]/48 # height's pixel number

#while(input() = 'q'):
last_x = 0;
last_y = 0;
while(True):
    time.sleep(0.01) 
    pos = m.position()
    x = -(pos[0] - filed[0]/2)
    y = (pos[1] - filed[1]/2)
    if abs(last_x - x) > 1:
	    d = np.sqrt(np.square(x)+np.square(y))
	    if y < 0:
	        d = -d
	    alpha = np.arctan(d/h)*180/np.pi
	    if y == 0:
	        beta = 0 
	    else:
	        beta = np.arctan(x/y)*180/np.pi
	    #print("1", flush=True)
	    print(alpha, beta, flush=True)
	    pitch.angle = alpha
	    yaw.angle = beta
	    last_x = x