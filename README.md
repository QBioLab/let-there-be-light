# Let-there-be-light
Track and light mouse

## Design on Khadas
remote control, graph control

1. [Framebuffer vncserver](https://github.com/ponty/framebuffer-vncserver)
2. [Set QT5 in Khadas VIM](https://docs.khadas.com/zh-cn/vim3/QT5Usage.html)
3. [PyQtGraph library](https://github.com/pyqtgraph/pyqtgraph)
4. [Assign fixed usb port name](https://www.freva.com/2019/06/20/assign-fixed-usb-port-names-to-your-raspberry-pi/)
5. [How to bind v4l2 USB cameras to the same device names even after reboot?](https://unix.stackexchange.com/questions/77170/how-to-bind-v4l2-usb-cameras-to-the-same-device-names-even-after-reboot)


## Device
CVT electronics IR Touchscreen
lusb: `lsusb : Bus 001 Device 003: ID 1ff7:0009 CVT Electronics.Co.,Ltd`
https://raspberrypi.stackexchange.com/questions/109211/rpi-hid-multitouch-invert-xy 
Get coordinates of touchscreen rawdata using Linux
https://stackoverflow.com/questions/28841139/how-to-get-coordinates-of-touchscreen-rawdata-using-linux

Linux kernel protocol
https://www.kernel.org/doc/html/v4.18/input/multi-touch-protocol.html


Add kernel support for I2C Mux(TCA9548A).

## ISSUSE
1. Gry drift

## ref
https://superuser.com/questions/497933/50-usb-webcams-in-a-single-computer-is-that-really-possible
