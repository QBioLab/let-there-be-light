import time
import cv2 as cv
import numpy as np
import libgimbal

"""
detecte mouse and laser point
"""

class mouseTracker:
    # 变量预设
    centroid_y = centroid_x = 0
    last_centroid_y = last_centroid_x = 0
    last_centroid_xy = [0, 0]
    ESC_flag = False
    count = 0
    track = False
    time_track = time.time()
    time_capture = time.time()
    track_stack = [0] * 2

    def __init__(self, gimbal_addr, camera_addr, roi):
        self.gimbal_addr = gimbal_addr
        self.camera_addr = camera_addr
        self.gimbal = libgimbal.gimbal(gimbal_addr)
        self.gimbal.park_gimbal()
        time.sleep(2)

        self.camera = cv.VideoCapture(self.gimbal_addr)
        self.camera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
        half_width = 370 / 2
        height = 220 / 200 * half_width * 2
        (x0, y0) = (95, -5)
        self.roi = roi  #[x0, x1, y0, y1]

    def detecte_laser(frame):
        blue_mask = cv.inRange(frame, (0, 0, 220), (255, 255, 255)) 
        #return centroid_blue_x, centroid_blue_y

    """HSV 遮罩"""
    def mask_red(hsv_frame):
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
    def mask_red_bgr(procession):
        lower_bgr = np.array([90, 110, 180])
        upper_bgr = np.array([120, 150, 240])
        mask_red_bgr = cv.inRange(procession, lower_bgr, upper_bgr)
        return mask_red_bgr

    """形态学处理"""
    def morphology_process(mask, erode1):
        morphology = cv.erode(mask, cv.getStructuringElement(cv.MORPH_ELLIPSE, (erode1, erode1)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (30, 30)))
        morphology = cv.erode(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (20, 20)))
        morphology = cv.dilate(morphology, cv.getStructuringElement(cv.MORPH_ELLIPSE, (10, 10)))
        return morphology

    """雲臺指向"""
    def point_gimbal(centroid_x, centroid_y, half_width, x0, y0):
        gimbal_x = centroid_x - half_width + x0
        gimbal_y = centroid_y - half_width + y0
        gimbal_pitch = 4096 - int(np.arctan2(np.sqrt(np.square(gimbal_x) + np.square(gimbal_y)), height) / np.pi * 8192)
        gimbal_yaw = int(np.arctan2(gimbal_y, gimbal_x) / np.pi * 8192)
        print("pitch, yaw:", gimbal_pitch, gimbal_yaw)
        self.gimbal.rotate_gimbal(gimbal_pitch, gimbal_yaw)

    def track_mouse(self):
        while(True): #TODO: add stop marker
            print("*", end="")
            ret, frame = self.camera.read()
            if not ret:
                continue
            procession = frame[60: 430, 55: 425]

            #HSV 遮罩
            hsv_frame = cv.cvtColor(procession, cv.COLOR_BGR2HSV)
            mask = mask_red(hsv_frame)
            if np.all(mask == 0):
                count = count + 1
                print('mask = None', count)
                track = False
                if count >= 500:
                    self.gimbal.rotate_gimbal(4096, 0)
                    time.sleep(0)
                    count = 0
                continue

            #形态学处理
            morphology = morphology_process(mask, 5)
            if np.all(morphology == 0):
                count = count + 1
                print('morphology = None', count)
                track = False
                if count >= 500:
                    self.gimbal.rotate_gimbal(4096, 0)
                    count = 0
                continue

            #画轮廓
            contour, hierarchy = cv.findContours(morphology, \
                    cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
            if len(contour) == 0:
                count = count + 1
                print('contour = None', count)
                track = False
                if count >= 500:
                    self.gimbal.rotate_gimbal(4096, 0)
                    count = 0
                continue

            #找质心
            moment = cv.moments(contour[-1])
            if moment['m00'] == 0:
                count = count + 1
                print('contour = Open', count)
                track = False
                if count >= 500:
                    self.gimbal.rotate_gimbal(4096, 0)
                    count = 0
                continue
            centroid_x = round(moment['m10'] / moment['m00'])
            centroid_y = round(moment['m01'] / moment['m00'])
            last_centroid_xy =  [centroid_x, centroid_y]
            track_stack = np.r_[track_stack, last_centroid_xy]
            if time.time() - time_track >= 3600:
                #np.savetxt("track_2/{current_time}.csv".format(current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')), track_stack, delimiter = ',')
                time_track = time.time()

            #畫跟蹤點
            track = True
            count = 0
            centroid_BGR = (0, 0, 255)
            centroid_result = cv.circle(procession, (centroid_x, centroid_y), 5, centroid_BGR, -1)
            print(track, centroid_x, centroid_y)
            if time.time() - time_capture >= 60:
                time_capture = time.time()
            dist_movement = np.sqrt(np.square(last_centroid_x - centroid_x) + np.square(last_centroid_y - centroid_y))
            if dist_movement > 0:
                point_gimbal(centroid_x, centroid_y, half_width, x0, y0)

        def close(self):
            self.camera.release()
            self.gimbal.close()

if __name__ == '__main__':
    track1 = mouseTracker("/dev/ttyUSB4", 1, [60,430,55,425])
    track1.track_mouse()
