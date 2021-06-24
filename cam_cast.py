import os
import sys
import cv2 as cv
import multiprocessing.connection

"""
open camera in seprated process and send image by socket
V0.1 hf 20210624
"""

class recorder:
    def __init__(self, cam_path):
        self.capture = cv.VideoCapture(cam_path)
        self.capture.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH,800);
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT,600);
        self.message = None

    def camera_export(self, argument):
        ret, self.frame = self.capture.read()
        if ret:
            self.message = {'image':self.frame}
            print("*", end="")
        return self.message

    def close(self, argument):
        self.capture.release()
        sys.exit()

    def unknown_command(self, argument):
        return('Unknow command')

if __name__ == '__main__':
    cam_idx = int(sys.argv[1])
    port = int(sys.argv[2])
    with multiprocessing.connection.Listener(('localhost', port), authkey=b'cancer') as server_cam:
        with server_cam.accept() as receiver:
            cam = recorder(cam_idx)
            message = None
            command = None
            argument = None
            command_mapping = {'close':cam.close, 'start':cam.camera_export,\
                    'live':cam.camera_export}
            while True:
                image = cam.camera_export('Null')
                if receiver.poll(timeout = 0.001):
                    message = receiver.recv()
                    command = command_mapping.get( message[0], cam.unknown_command)
                    argument = message[1]
                    if message[0] == 'live':
                        #receiver.send( command(argument) )
                        receiver.send( image )
                        print("-", end="")
                    else:
                        command(argument)
                        #TODO: if lose connection, kill this process
