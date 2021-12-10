import time
import DPS832

dp1 = DPS832.DP832("USB0::6833::3601::DP8C230600574::0::INSTR")
#dp1 = dp832.dp832(fname="/dev/usbtmc0")
dp2 = DPS832.DP832("USB0::6833::3601::DP8C211000635::0::INSTR")
#dp2 = dp832.dp832(fname="/dev/usbtmc1")

illumination = "On"

def on():
    dp1.toggle_output(2, 1)
    dp1.toggle_output(3, 1)
    dp2.toggle_output(1, 1)
    dp2.toggle_output(2, 1)
    dp2.toggle_output(3, 1)

def off():
    dp1.toggle_output(2, 0)
    dp1.toggle_output(3, 0)
    dp2.toggle_output(1, 0)
    dp2.toggle_output(2, 0)
    dp2.toggle_output(3, 0)



if __name__ == '__main__':
    while True:
        now = time.strftime("%H:%M", time.localtime())
        if now == "08:00" and illumination == "Off":
            illumination = "On"
            #print(illumination)
            print("Turn on at", now)
            on()


        if now == "20:00" and illumination == "On":
            illumination = "Off"
            off()
            print("Turn off at", now)

        time.sleep(1)# refresh time 1s
