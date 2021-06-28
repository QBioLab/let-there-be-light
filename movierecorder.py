import sys
import cv2

if __name__ == '__main__':
    val = True
    idx = int(sys.argv[1])
    cap = cv2.VideoCapture(idx)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    out = cv2.VideoWriter("record-"+str(idx)+".avi", fourcc, 20.0, (640, 480), True)

    while val is True:
        ret, frame = cap.read()
        cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        if frame is None:
            break
        else:
            out.write(frame)
            print("*", end="")

    cap.release()
    out.release()
