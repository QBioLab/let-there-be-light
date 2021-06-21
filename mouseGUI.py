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
#from PyQt5.QtGui import QPixmap

class fireball(QWidget):
    def __init__(self):
        super(fireball, self).__init__()
        self.load_ui()
        self.current_box = 1
        self.timer_on = True
        self.connect2slot()
        self.box1 = None
        self.display_width = 1200 #800*1.5
        self.display_height = 900 #600*1.5
        self.tracker_on = False
        timer = QTimer(self)
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

    """Update checkbox button status"""
    @pyqtSlot()
    def update_status(self, id):
        self.current_box = id
        self.print2console("Switch to box %i"%self.current_box)

    @pyqtSlot()
    def start_track(self):
        """start tracking process on certain box"""
        if self.current_box == 1:
            #subprocess.Popen(['python3', f'{os.getcwd()}/camRecorder.py'])
            self.box1 = multiprocessing.connection.Client(('localhost', 6003), authkey=b'cancer')
            self.tracker_on = True
        self.print2console("Start track on box %i"%self.current_box)

    @pyqtSlot()
    def stop_track(self):
        """stop tracking process on certain box"""
        self.box1.send(['close', 'Null'])
        self.box1.close()
        self.tracker_on = False
        self.print2console("Stop track on box %i"%self.current_box)

    @pyqtSlot()
    def update_image(self):
        """update image_label with a new opencv image"""
        if self.tracker_on :
            self.image_label.setPixmap(self.get_image())


    def get_image(self):
        """revceive image and covert to QPixmap"""
        self.box1.send(['live', 'Null'])
        img = self.box1.recv()['image']
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)#['image'][..., ::-1]
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


if __name__ == "__main__":
    app = QApplication([])
    widget = fireball()
    widget.show()
    sys.exit(app.exec_())
