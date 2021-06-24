import time
import dp832
import mouseTracker

dp1 = dp832.dp832(fname="/dev/usbtmc0")
dp2 = dp832.dp832(fname="/dev/usbtmc1")
track1 = mouseTracker("/dev/ttyUSB0", 0, [60, 430, 55, 425])
track2 = mouseTracker("/dev/ttyUSB1", 4, [60, 430, 55, 425])
track3 = mouseTracker("/dev/ttyUSB2", 8, [60, 430, 55, 425])
track4 = mouseTracker("/dev/ttyUSB3", 12, [60, 430, 55, 425])

illumination = "On"

while True:
    now = time.strftime("%H:%M", time.localtime())

    if now == "08:00" and illumination == "Off":
        illumination = "On"
        dp1.AllOn()
        dp2.AllOn()
        track1.track_mouse()
        track2.track_mouse()
        track3.track_mouse()
        track4.track_mouse()

    if now == "20:00" and illumination == "On":
        illumination = "Off"
        dp1.AllOff()
        dp2.AllOff()
        track1.close()
        track2.close()
        track3.close()
        track4.close()