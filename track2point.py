#!/bin/python3
import sys
import json
import pointer
import tracker
import multiprocessing.connection

"""Usage
1. `python3 track2point.py` load build-in parameters and track in cli-only
2. `python3 track2point.py xxx.json` load configuration file and track in cli-only
3. `python3 track2point.py xxx.json socket` load configuration file and display
    in mouseGUI mode
4. `python3 track2point.py xxx.json disp` load configuration file and display
    in integrated window mode

v0.1 first version by hf
"""

# CONSTANT MARKER
FAIL = 0 # lost camera connection
MOVE = 1 # apply track
PARK = 2 # park pointer
LOST = 3 # lost mouse
IGNO = 4 # ignore tracking result

# default configure value
cam_idx = 0
roi_x0 = 0  
roi_x1 = 600
roi_y0 = 0
roi_y1 = 600
gimbal_enable = False
gimbal_path = "/dev/ttyUSB0"
gimbal_pos_x0 = 75
gimbal_pos_y0 = -5
gimbal_half_width = 370/2
gimbal_mm_height = 210 / 200 * gimbal_half_width * 2
yaw_bias = 0
erode1 = 5
log_dir = "/dev/null"
# TODO: change to unix domain socket for better performance

def init_config():
    port = "" # socket port get from argv, zero means only cli
    if len(sys.argv) == 1:
        print("Using default configuration and dump to file, config.json")
        config = {'cam_idx':cam_idx, 'roi_x0':roi_x0, 'roi_y0':roi_y0, 'roi_x1':roi_x1, \
            'roi_y1':roi_y1, 'gimbal_enable':gimbal_enable, 'gimbal_path':gimbal_path, \
            'gimbal_path':gimbal_path, 'gimbal_pos_x0':gimbal_pos_x0, \
            'gimbal_pos_y0':gimbal_pos_y0, 'gimbal_half_width':gimbal_half_width, \
            'gimbal_mm_height':gimbal_mm_height, 'log_dir':log_dir, 'yaw_bias':yaw_bias,\
            'erode1':5}
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        return port, config
    elif len(sys.argv) > 1:
        config_file = sys.argv[1]
        try:
            print("Loading configuration from file") 
            with open(config_file, 'r') as file:
                config = json.load(file)
                # TODO: Check value error and JSON format
                if len(sys.argv) == 3: # get port number by passed argument
                    port = sys.argv[2]
                return port, config
        except:
            print("Unexpected error:", sys.exc_info()[0])

if __name__=='__main__':
    port, config = init_config()
    finder = tracker.MouseTracker(config['cam_idx'], [config[i] for i in \
            ['roi_x0', 'roi_x1', 'roi_y0', 'roi_y1']])
    finder.set_data_dir(config['log_dir'])
    finder.set_erode1(config['erode1'])
    if config['gimbal_enable']:
        light = pointer.Pointer(config['gimbal_path'])
        light.set_pointer(config['gimbal_pos_x0'], config['gimbal_pos_y0'], \
            config['gimbal_half_width'], config['gimbal_mm_height'], config['yaw_bias'])
    if port == "": #TODO: add integrated interface mode
        print("Entering cli-only mode")
        while True:
            ret, pos, image = finder.track_mouse()
            if ret == MOVE and config['gimbal_enable']:
                light.point2mouse(pos[0], pos[0])
                print("Found at", pos[0], pos[1])
    elif port == "disp":
        print("Entering cli with integrated mode")
        import cv2 as cv
        while True:
            ret, pos, image = finder.track_mouse()
            print(ret)
            if not (ret == FAIL):
                cv.imshow('Mouse Tracker', image)
            if ret == MOVE and config['gimbal_enable']:
                light.point2mouse(pos[0], pos[1])
            if cv.waitKey(1) == 27:
                break
        finder.close()
        cv.destroyAllWindows()

    else: # send image to  mosueGUI
        print("Entering mouseGUI model")
        with multiprocessing.connection.Listener(('localhost', int(port)), authkey=b'cancer') as tracker_server:
            with tracker_server.accept() as receiver:
                message = None
                command = None
                while True:
                    ret, pos, image = finder.track_mouse()
                    if ret == MOVE and config['gimbal_enable']:
                        light.point2mouse(pos[0], pos[1])
                    if receiver.poll(timeout = 0.003): # blocking or non-blocking
                        message = receiver.recv()
                        argument = message[1]
                        if message[0] == 'live' and ret != FAIL:
                            receiver.send( image )
                        elif message[0] == 'close':
                            finder.close()
                            break
                        elif message[0] == 'pause':
                            print("stop gimbal, but keep camera open")
                            light.disconnect()
                        elif message[0] == 'resume':
                            print("resume gimbal")
                            light.connect()
                        else:
                            print("I don't know your command:", message[0])
                            #TODO: if lose connection, kill this process
