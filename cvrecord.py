import cv2 as cv

capture = cv.VideoCapture(0)
count = 0

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    cv.imshow('test', frame)
    if cv.waitKey(1) == 27:
        break
    if count == 30:
        cv.imwrite("test.tiff", frame)
        break

cv.destroyAllWindows()
capture.release()

