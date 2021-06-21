import os
import sys
import cv2 as cv
import multiprocessing.connection


class recorder:
    def __init__(self, cam_path):
        self.capture = cv.VideoCapture(cam_path)
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
    with multiprocessing.connection.Listener(('localhost', 6003), authkey=b'cancer') as server_cam:
        with server_cam.accept() as receiver:
            cam = recorder(0)
            message = None
            command = None
            argument = None
            command_mapping = {'close':cam.close, 'start':cam.camera_export,\
                    'live':cam.camera_export}
            while True:
                if receiver.poll(timeout = 0.001):
                    message = receiver.recv()
                    command = command_mapping.get( message[0], cam.unknown_command)
                    argument = message[1]
                    if message[0] == 'live':
                        receiver.send( command(argument) )
                        print("-", end="")
                    else:
                        command(argument)
                        #TODO: if lose connection, kill this process
