import time
import cv2 as cv
import numpy as np
import libgimbal

"""
detecte mouse and laser point
V0.1 orignal work by zhangyi
V0.2 package to class
"""

class mouseTracker:

    def __init__(self, gimbal_addr, camera_addr, roi, mm_height, x0, y0):
        # initialize gimbal
        self.gimbal_addr = gimbal_addr
        self.gimbal = libgimbal.gimbal(gimbal_addr)
        self.gimbal.park_gimbal()
        time.sleep(2)

        # initialize camera
        self.camera_addr = camera_addr
        self.camera = cv.VideoCapture(self.camera_addr)
        self.camera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
        # ref: https://github.com/opencv/opencv/issues/9540

        # 变量预设
        self.half_width = 370 / 2
        self.height = mm_height / 200 * self.half_width * 2
        self.x0 = x0
        self.y0 = y0
        self.roi = roi  #[x0, x1, y0, y1]
        self.centroid_y = self.centroid_x = 0
        self.last_centroid_y = self.last_centroid_x = 0
        self.count = 0
        self.time_track = time.time()
        self.time_capture = time.time()
        self.track_stack = [0] * 2
        self.track = False


    def detecte_laser(self, frame):
        blue_mask = cv.inRange(frame, (0, 0, 220), (255, 255, 255)) 
        #return centroid_blue_x, centroid_blue_y

    """HSV 遮罩"""
    def mask_red(self, hsv_frame):
        hsv_h_range = [0, 10, 156, 180]
        hsv_s_range = [100, 250]
        hsv_v_range = [60, 250]
        lower_hsv0 = np.array([hsv_h_range[0], hsv_s_range[0], hsv_v_range[0]])
        upper_hsv0 = np.array([hsv_h_range[1], hsv_s_range[1], hsv_v_range[1]])
        lower_hsv1 = np.array([hsv_h_range[2], hsv_s_range[0], hsv_v_range[0]])
        upper_hsv1 = np.array([hsv_h_range[3], hsv_s_range[1], hsv_v_range[1]])
        mask0 = cv.inRange(hsv_frame, lower_hsv0, upper_hsv0)
        mask1 = cv.inRange(hsv_frame, lower_hsv1, upper_hsv1)
        mask_red = mask0 + mask1
        return mask_red
    
    """BGR 遮罩"""
    def mask_red_bgr(self, procession):
        lower_bgr = np.array([90, 110, 180])
        upper_bgr = np.array([120, 150, 240])
        mask_red_bgr = cv.inRange(procession, lower_bgr, upper_bgr)
        return mask_red_bgr

    """形态学处理"""
    def morphology_process(self, mask, erode1):
        morphology = cv.erode(mask, cv.getStructuringElement(cv.MORPH_ELLIPSE, (erode1, erode1)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (30, 30)))
        morphology = cv.erode(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (20, 20)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (10, 10)))
        return morphology

    """雲臺指向"""
    def point_gimbal(self, centroid_x, centroid_y):
        gimbal_x = centroid_x - self.half_width + self.x0
        gimbal_y = centroid_y - self.half_width + self.y0
        gimbal_pitch = 4096 - int(np.arctan2(np.sqrt(np.square(gimbal_x) + np.square(gimbal_y)), \
                self.height) / np.pi * 8192)
        gimbal_yaw = int(np.arctan2(gimbal_y, gimbal_x) / np.pi * 8192)
        print("pitch, yaw:", gimbal_pitch, gimbal_yaw)
        self.gimbal.rotate_gimbal(gimbal_pitch, gimbal_yaw)

    def track_mouse(self):
        """ main function for tracking"""
        print("*", end="")
        ret, frame = self.camera.read()
        if not ret:
            return False, None
        procession = frame[self.roi[0]: self.roi[1], self.roi[2]: self.roi[3]]

        #HSV 遮罩
        hsv_frame = cv.cvtColor(procession, cv.COLOR_BGR2HSV)
        mask = self.mask_red(hsv_frame)
        if np.all(mask == 0):
            self.count = self.count + 1
            print('mask = None', self.count)
            self.track = False
            if self.count >= 500:
                self.gimbal.rotate_gimbal(4096, 0)
                time.sleep(0)
                self.count = 0
            return False, None

        #形态学处理
        morphology = self.morphology_process(mask, 5)
        if np.all(morphology == 0):
            self.count = self.count + 1
            print('morphology = None', count)
            self.track = False
            if count >= 500:
                self.gimbal.rotate_gimbal(4096, 0)
                count = 0
            return False, None

        #画轮廓
        contour, hierarchy = cv.findContours(morphology, cv.RETR_CCOMP, \
                cv.CHAIN_APPROX_NONE)
        if len(contour) == 0:
            self.count = self.count + 1
            print('contour = None', self.count)
            self.track = False
            if self.count >= 500:
                self.gimbal.rotate_gimbal(4096, 0)
                self.count = 0
            return False, None

        #找质心
        moment = cv.moments(contour[-1])
        if moment['m00'] == 0:
            self.count = self.count + 1
            print('contour = Open', self.count)
            self.track = False
            if self.count >= 500:
                self.gimbal.rotate_gimbal(4096, 0)
                self.count = 0
            return False, None
        self.centroid_x = round(moment['m10'] / moment['m00'])
        self.centroid_y = round(moment['m01'] / moment['m00'])
        #TODO: save centroid_x
        self.track_stack = np.r_[self.track_stack, [self.centroid_x, self.centroid_y]]
        if time.time() - self.time_track >= 3600:
            #np.savetxt("track_2/{current_time}.csv".format(current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')), track_stack, delimiter = ',')
            self.time_track = time.time()

        #畫跟蹤點
        self.track = True
        self.count = 0
        centroid_BGR = (0, 0, 255)
        centroid_result = cv.circle(procession, (self.centroid_x, self.centroid_y), 5, centroid_BGR, -1)
        print(self.track, self.centroid_x, self.centroid_y)
        if time.time() - self.time_capture >= 60:
            self.time_capture = time.time()
        dist_movement = np.sqrt(np.square(self.last_centroid_x - self.centroid_x) \
                + np.square(self.last_centroid_y - self.centroid_y))
        if dist_movement > 0:
            self.point_gimbal(self.centroid_x, self.centroid_y)
            self.last_centroid_x = slef.centroid_x
            self.last_centroid_y = slef.centroid_y
        return True, centroid_result

    def close(self, argument):
        self.camera.release()
        self.gimbal.close()

if __name__ == '__main__':
    argv_file = sys.argv[1] #TODO: load configuration file
    port = int(sys.argv[2])
    with multiprocessing.connection.Listener(('localhost', port), authkey=b'cancer') as server_cam:
    ¦   with server_cam.accept() as receiver:
            tracker = mouseTracker("/dev/ttyS0", 0, [60,430,55,425], 10, 10, 20)
    ¦   ¦   message = None
    ¦   ¦   command = None
    ¦   ¦   argument = None
    ¦   ¦   command_mapping = {'close':tracker.close, 'live':tracker.camera_export}
    ¦   ¦   while True:
                ret, image = tracker.track_mouse()
    ¦   ¦   ¦   if receiver.poll(timeout = 0.001):
    ¦   ¦   ¦   ¦   message = receiver.recv()
    ¦   ¦   ¦   ¦   command = command_mapping.get( message[0], cam.unknown_command)
    ¦   ¦   ¦   ¦   argument = message[1]
    ¦   ¦   ¦   ¦   if message[0] == 'live':
    ¦   ¦   ¦   ¦   ¦   receiver.send( image )
    ¦   ¦   ¦   ¦   ¦   #print("-", end="")
    ¦   ¦   ¦   ¦   else:
    ¦   ¦   ¦   ¦   ¦   command(argument)
    ¦   ¦   ¦   ¦   ¦   #TODO: if lose connection, kill this process
