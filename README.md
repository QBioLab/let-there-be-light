# Let-there-be-light
Track and light mouse

## Control and Computing Unit with Khadas 控制和运算单元
Target: remote control, graph interface

Khadas VIM3 don't shop the kernel with usbtmc and i2c mux driver, so I
[rebuild kernel](https://docs.khadas.com/vim3/HowToUpgradeTheKernel.html)
inside [fenix's docker](https://github.com/khadas/fenix).
The usbtmc and i2c mux are package as module, I load [module automatic with systemd](https://wiki.archlinux.org/title/Kernel_module)
by add `usbtmc` and `i2c_mux_pca954x` to `/etc/modules-load.d/modules.conf`.

Only one USB bus is exported in VIM3, I try to use orignal M.2 port as PCI-e
port. I install ADT-Link's [M.2 NVMe to PCIe X1 extender](http://www.adtlink.cn/en/product/R41.html)
on Khadas M.2 extender board, then a PCIe Card(VIA VL805). The PCIe card is
power by sperated 5V instead of on-board 5V. But system only reconginze this
card as USB2 bus. Why? May I also feed 12v pin. Once I mount USB3 device,
system will reboot. 

1. [Framebuffer vncserver](https://github.com/ponty/framebuffer-vncserver)
2. [Set QT5 in Khadas VIM](https://docs.khadas.com/zh-cn/vim3/QT5Usage.html)
3. [PyQtGraph library](https://github.com/pyqtgraph/pyqtgraph)
4. [Assign fixed usb port name](https://www.freva.com/2019/06/20/assign-fixed-usb-port-names-to-your-raspberry-pi/)
5. [How to bind v4l2 USB cameras to the same device names even after reboot?](https://unix.stackexchange.com/questions/77170/how-to-bind-v4l2-usb-cameras-to-the-same-device-names-even-after-reboot)
6. [Convert M.2 to PCI-e in VIM3](https://forum.khadas.com/t/pci-e-card-power-supply/12122)

## Device
CVT electronics IR Touchscreen
lusb: `lsusb : Bus 001 Device 003: ID 1ff7:0009 CVT Electronics.Co.,Ltd`
https://raspberrypi.stackexchange.com/questions/109211/rpi-hid-multitouch-invert-xy 
Get coordinates of touchscreen rawdata using Linux
https://stackoverflow.com/questions/28841139/how-to-get-coordinates-of-touchscreen-rawdata-using-linux

Linux kernel protocol
https://www.kernel.org/doc/html/v4.18/input/multi-touch-protocol.html



### Gimbal design and setting

Before run SimpleBGC in khadas, please install `librxtx-java`

## ISSUSE
1. Gry drift

## ref
https://superuser.com/questions/497933/50-usb-webcams-in-a-single-computer-is-that-really-possible
