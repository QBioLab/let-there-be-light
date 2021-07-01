#!/bin/python3
# This Python file uses the following encoding: utf-8
import sys
import os
import time
import numpy as np
import subprocess
import multiprocessing.connection

from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget 
from PyQt5.QtCore import QFile, pyqtSlot, QTimer, Qt

import scheduler

"""
GUI for tracking mouse
v0.1 hf 20210628
"""

class fireball(QWidget):
    def __init__(self):
        super(fireball, self).__init__()
        self.load_ui()
        self.current_cage = 1
        self.scheduler_on = True
        self.all_cage = [Cage(1), Cage(2), Cage(3), Cage(4)]
        self.display_width = 1200 #800*1.5
        self.display_height = 900 #600*1.5,, 370*3?
        self.connect2slot()
        timer_image = QTimer(self.image_label)
        timer_image.timeout.connect(self.update_image)
        timer_image.start(2)
        timer_scheduler = QTimer(self)
        timer_scheduler.timeout.connect(self.run_scheduler)
        timer_scheduler.start(30000)
        self.__done= False

    def connect2slot(self):
        self.schedulerON.toggled.connect(self.set_scheduler)
        self.onButton.clicked.connect(self.start_track)
        self.offButton.clicked.connect(self.stop_track)
        self.exitButton.clicked.connect(self.close)
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
        self.current_cage = id
        self.print2console("Switch to box %i"%self.current_cage)

    @pyqtSlot()
    def start_track(self):
        """start tracking process on certain box"""
        portmap = [6000, 6001, 6002, 6003]
        config_files = ["cage1_config.json", "cage2_config.json", \
                "cage3_config.json", "cage4_config.json"]
        uid = self.current_cage - 1 
        if not self.all_cage[uid].on :
            subprocess.Popen(['python3', f'{os.getcwd()}/track2point.py', \
                str(config_files[uid]), str(portmap[uid])])
            time.sleep(2)
            # TODO: check connection
            self.all_cage[uid].cilent = multiprocessing.connection.Client(\
                ('localhost', portmap[uid]), authkey=b'cancer')
            self.all_cage[uid].on = True
            self.all_cage[uid].gimbal_on = True # TODO: get from return information
            self.print2console("Start track on cage %i"%(uid+1))
        else:
            self.print2console("Fail to start track on cage%i, \
                please try again"%(uid+1))

    @pyqtSlot()
    def stop_track(self):
        """stop running track process"""
        uid =  self.current_cage - 1
        if self.all_cage[uid].on:
            self.all_cage[uid].cilent.send(['close', 'Null'])
            self.all_cage[uid].cilent.close()
            self.all_cage[uid].on = False
            self.print2console("Stop track on box %i"%(uid+1))
        else:
            self.print2console("Tracking have not been executed in Cage%i"%(uid+1))

    @pyqtSlot()
    def update_image(self):
        """update image_label with a new opencv image"""
        uid = self.current_cage - 1
        if self.all_cage[uid].on:
            self.image_label.setPixmap(self.get_image())

    def get_image(self):
        """revceive image and covert to QPixmap"""
        uid = self.current_cage - 1
        self.all_cage[uid].cilent.send(['live', 'Null'])
        img = self.all_cage[uid].cilent.recv()#['image']
        img = img[..., ::-1].copy()
        h, w, ch = img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height,\
                Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    @pyqtSlot()
    def set_scheduler(self):
        """set and turn on/off schedule """
        if self.schedulerON.isChecked():
            self.scheduler_on = True
            self.print2console("Turn on scheduler")
        else:
            self.scheduler_on = False
            self.print2console("Turn off scheduler")

    @pyqtSlot()
    def run_scheduler(self):
        """Run scheduler in QTimer"""
        if self.scheduler_on:
            now = time.strftime("%H:%M", time.localtime())
            # TODO: handle connection error
            # TODO: update clock setting from GUI
            if now == "08:00" and self.__done == False:
                scheduler.on()
                for cage in range(1, 5):
                    self.current_cage = cage
                    self.start_track()
                self.print2console("Turn on at %s"%now)
                self.__done = True
            elif now == "20:00" and self.__done == False:
                scheduler.off()
                for cage in range(1, 5):
                    self.current_cage = cage
                    self.stop_track()
                self.print2console("Turn on off %s"%now)
                self.__done = True
            else:
                self.__done = False

    @pyqtSlot()
    def close(self):
        """close GUI"""
        self.print2console("Closing mouseGUI")
        for cage in range(1, 5):
            self.current_cage = cage
            self.stop_track()
        sys.exit(0)

    def print2console(self, text):
        """format output"""
        timestamp = time.strftime("%m-%d %H:%M", time.localtime())
        output = timestamp +": "+text
        self.outputConsole.append(output)
        print(output)

class Cage:
    """Information of tracker"""
    def __init__(self, id):
        self.uid = id
        self.on = False
        self.cilent = None
        self.gimbal_on = False

if __name__ == "__main__":
    app = QApplication([])
    widget = fireball()
    if len(sys.argv) > 1:
        if sys.argv[1] == '-full' :
            widget.showFullScreen()
    widget.show()
    sys.exit(app.exec_())
