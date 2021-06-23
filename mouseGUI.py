# This Python file uses the following encoding: utf-8
import sys
import os
import time
#import cv2 
import numpy as np
import subprocess
import multiprocessing.connection

from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget 
from PyQt5.QtCore import QFile, pyqtSlot, QTimer, Qt

class fireball(QWidget):
    def __init__(self):
        super(fireball, self).__init__()
        self.load_ui()
        self.current_box = 1
        self.timer_on = True
        self.all_box = [Box(1), Box(2), Box(3), Box(4)]
        self.display_width = 1200 #800*1.5
        self.display_height = 900 #600*1.5
        self.connect2slot()
        timer = QTimer(self.image_label)
        timer.timeout.connect(self.update_image)
        timer.start(0)

    def connect2slot(self):
        self.onTimer.toggled.connect(self.schedule)
        self.onButton.clicked.connect(self.start_track)
        self.offButton.clicked.connect(self.stop_track)
        self.boxButton_1.clicked.connect(lambda: self.update_status(1))
        self.boxButton_2.clicked.connect(lambda: self.update_status(2))
        self.boxButton_3.clicked.connect(lambda: self.update_status(3))
        self.boxButton_4.clicked.connect(lambda: self.update_status(4))

    def load_ui(self):
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

    @pyqtSlot()
    def update_status(self, id):
        """Update checkbox button status"""
        self.current_box = id
        self.print2console("Switch to box %i"%self.current_box)

    @pyqtSlot()
    def start_track(self):
        """start tracking process on certain box"""
        portmap = [6000, 6001, 6002, 6003]
        camport = [0, 4, 6, 8]
        uid = self.current_box - 1 
        if not self.all_box[uid].on :
            subprocess.Popen(['python3', f'{os.getcwd()}/camRecorder.py', \
                str(camport[uid]), str(portmap[uid])])
            time.sleep(1)
            print(portmap[uid])
            self.all_box[uid].cilent = multiprocessing.connection.Client(\
                ('localhost', portmap[uid]), authkey=b'cancer')
            self.all_box[uid].on= True
            self.print2console("Start track on box %i"%(uid+1)
        else:
            self.print2console("Fail to start track on box %i, \
                please try again"%(uid+1))

    @pyqtSlot()
    def stop_track(self):
        """stop running track process"""
        uid =  self.current_box - 1
        if self.all_box[uid].on:
            self.all_box[uid].cilent.send(['close', 'Null'])
            self.all_box[uid].cilent.close()
            self.all_box[uid].on = False
            self.print2console("Stop track on box %i"%(uid+1))
        else:
            self.print2console("Tracking have not been executed in Box %i"%(uid+1))

    @pyqtSlot()
    def update_image(self):
        """update image_label with a new opencv image"""
        uid = self.current_box - 1
        if self.all_box[uid].on:
            self.image_label.setPixmap(self.get_image())

    def get_image(self):
        """revceive image and covert to QPixmap"""
        uid = self.current_box - 1
        self.all_box[uid].cilent.send(['live', 'Null'])
        img = self.all_box[uid].cilent.recv()['image']
        img = img[..., ::-1].copy()
        h, w, ch = img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height,\
                Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    """schedule running time"""
    @pyqtSlot()
    def schedule(self):
        if self.onTimer.isChecked():
            self.timer_on = True
            self.print2console("Turn on timer")
        else:
            self.timer_on = False
            self.print2console("Turn off timer")

    """format output"""
    def print2console(self, text):
         timestamp = time.strftime("%m-%d %H:%M", time.localtime())
         output = timestamp +": "+text
         self.outputConsole.append(output)
         print(output)

class Box:
    """Information of tracker"""
    def __init__(self, id):
        self.uid = id
        self.on = False
        self.cilent = None

if __name__ == "__main__":
    app = QApplication([])
    widget = fireball()
    widget.show()
    sys.exit(app.exec_())
