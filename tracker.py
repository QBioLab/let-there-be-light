import os
import time
import cv2 as cv
import numpy as np

"""
detecte mouse and laser point
V0.1 orignal work by zhangyi
V0.2 package to class
"""

FAIL = 0 # lost camera connection
MOVE = 1 # apply track
PARK = 2 # park pointer
LOST = 3 # lost mouse
IGNO = 4 # ignore tracking result

class MouseTracker:
    def __init__(self, camera_addr, roi):
        # initialize camera
        self.camera_addr = camera_addr
        try:
            self.camera = cv.VideoCapture(self.camera_addr)
        except Exception as error:
            print("Fail to open camera", self.camera_addr,":", error)
        # use MJPG to low cost of USB bandwidth 
        # ref: https://github.com/opencv/opencv/issues/9540
        self.camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv.CAP_PROP_FPS, 25)
        self.camera.set(cv.CAP_PROP_AUTO_EXPOSURE, 1) # 1 for manual mode
        self.camera.set(cv.CAP_PROP_EXPOSURE, 100)
        #cam.set(cv.CAP_PROP_AUTO_WB, 0)
        fourcc = cv.VideoWriter_fourcc(*"MJPG")
        self.camera.set(cv.CAP_PROP_FOURCC, fourcc)
        # initialize video recorder
        self.save_moive = False
        self.save_fps = 5
        self.save_dir = "/dev/null"
        self.roi = roi  #[y0, y1, x0, x1]
        self.erode1 = 5
        self.centroid_y = self.centroid_x = 0
        self.last_centroid_y = self.last_centroid_x = 0
        self.count = 0
        self.last_time= time.time()

    def detecte_laser(self, frame):
        blue_mask = cv.inRange(frame, (0, 0, 220), (255, 255, 255)) 
        #return centroid_blue_x, centroid_blue_y

    def mask_red(self, hsv_frame):
        """HSV 遮罩"""
        hsv_h_range = [0, 10, 156, 180]
        hsv_s_range = [100, 250]
        hsv_v_range = [50, 200]
        lower_hsv0 = np.array([hsv_h_range[0], hsv_s_range[0], hsv_v_range[0]])
        upper_hsv0 = np.array([hsv_h_range[1], hsv_s_range[1], hsv_v_range[1]])
        lower_hsv1 = np.array([hsv_h_range[2], hsv_s_range[0], hsv_v_range[0]])
        upper_hsv1 = np.array([hsv_h_range[3], hsv_s_range[1], hsv_v_range[1]])
        mask0 = cv.inRange(hsv_frame, lower_hsv0, upper_hsv0)
        mask1 = cv.inRange(hsv_frame, lower_hsv1, upper_hsv1)
        mask_red = mask0 + mask1
        return mask_red

    def set_mask_red(self):
        """Set mask parameters"""
        print("Set HSV filter parameters")
    
    def mask_red_bgr(self, procession):
        """BGR 遮罩"""
        lower_bgr = np.array([90, 110, 180])
        upper_bgr = np.array([120, 150, 240])
        mask_red_bgr = cv.inRange(procession, lower_bgr, upper_bgr)
        return mask_red_bgr

    def set_erode1(self, erode1):
        self.erode1 = erode1

    def morphology_process(self, mask, erode1):
        """形态学处理"""
        morphology = cv.erode(mask, cv.getStructuringElement(cv.MORPH_ELLIPSE, \
                (self.erode1, self.erode1)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (30, 30)))
        morphology = cv.erode(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (20, 20)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (10, 10)))
        return morphology

    def track_mouse(self):
        """track red spot on mouse frame by frame
        return: result, position, image 
        """
        ret, frame = self.camera.read()
        if not ret:
            return FAIL, None, None
        #[y0:y1, x0:x1]
        procession = frame[self.roi[0]: self.roi[1], self.roi[2]: self.roi[3]]
        self.save_data(procession)

        #HSV 遮罩
        hsv_frame = cv.cvtColor(procession, cv.COLOR_BGR2HSV)
        mask = self.mask_red(hsv_frame)
        if np.all(mask == 0):
            self.count = self.count + 1
            print('mask = None', self.count)
            if self.count >= 500:
                self.count = 0
                return PARK, None, procession
            return LOST, None, procession

        #形态学处理
        morphology = self.morphology_process(mask, self.erode1)
        if np.all(morphology == 0):
            self.count = self.count + 1
            print('morphology = None', self.count)
            if self.count >= 500:
                self.count = 0
                return PARK, None, procession
            return LOST, None, procession

        #画轮廓
        contour, hierarchy = cv.findContours(morphology, cv.RETR_CCOMP,\
                cv.CHAIN_APPROX_NONE)
        if len(contour) == 0:
            self.count = self.count + 1
            print('contour = None', self.count)
            if self.count >= 500:
                self.count = 0
                return PARK, None, procession
            return LOST, None, procession

        #找质心
        moment = cv.moments(contour[-1])
        if moment['m00'] == 0:
            self.count = self.count + 1
            print('contour = Open', self.count)
            if self.count >= 500:
                self.count = 0
                return PARK, None, procession
            return LOST, None, procession
        self.centroid_x = round(moment['m10'] / moment['m00'])  
        self.centroid_y = round(moment['m01'] / moment['m00']) 

        #畫跟蹤點
        self.count = 0
        centroid_BGR = (0, 0, 255)
        centroid_result = cv.circle(procession, (self.centroid_x, self.centroid_y), 5, centroid_BGR, -1)
        #print("Found mouse at:", self.centroid_x, self.centroid_y)
        dist_movement = np.sqrt(np.square(self.last_centroid_x - self.centroid_x) \
            + np.square(self.last_centroid_y - self.centroid_y))
        if dist_movement > 0:
            self.last_centroid_x = self.centroid_x
            self.last_centroid_y = self.centroid_y
            return MOVE, [self.centroid_x + self.roi[2], 
                self.centroid_y + self.roi[0]], centroid_result
            #print(self.centroid_x, self.centroid_y)
            #return MOVE, [self.centroid_x, self.centroid_y], centroid_result
        return IGNO, None, centroid_result

    def set_data_dir(self, directory):
        record_time = time.strftime("%Y%m%d-%H%M", time.localtime())
        self.save_moive = True
        self.save_dir = directory
        fourcc = cv.VideoWriter_fourcc(*"MJPG")
        height = self.roi[1] - self.roi[0]
        width = self.roi[3] - self.roi[2]
        self.check_dir(directory)
        self.out = cv.VideoWriter(self.save_dir+"/record-"+str(self.camera_addr)\
            +"-"+record_time+".mkv", fourcc, self.save_fps, (width, height))

    def check_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_data(self, image):
        """save image and centroid to file in period"""
        if self.save_moive and time.time()-self.last_time > 1/self.save_fps: 
            self.last_time = time.time()
            #self.out.write(cv.cvtColor(image, cv.COLOR_RGB2BGR))
            self.out.write(image)
            #result.write(centroid[0] centroid[1])

    def close(self):
        self.camera.release()
        self.out.release()
        #print("release camera")

if __name__ == '__main__':
    #tracker = MouseTracker("test/record-0.avi", [170, 520, 90, 510])
    tracker = MouseTracker(0, [70, 440, 45, 415])
    ret = True
    while ret:
        ret, centroid, image = tracker.track_mouse()
        cv.imshow('Mouse Tracker', image)
        if cv.waitKey(1) == 27:
             break
    tracker.close()
    cv.destroyAllWindows()
