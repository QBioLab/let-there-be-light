# Let there be light
Track and light mouse

## Control and Computing Unit with Khadas 控制和运算单元
Target: enable to remote controll, graph interface, error handle

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

TODO: assign fixed camera path to specifical usb port. Device info could get
from `udevadm info -a -p  $(udevadm info -q path -n /dev/video0)`

TODO: organize output information
TODO: send command to power supply then release and return.

Build GUI in QT. 


Reference:
- [PyQtGraph library](https://github.com/pyqtgraph/pyqtgraph)
- [Assign fixed usb port name](https://www.freva.com/2019/06/20/assign-fixed-usb-port-names-to-your-raspberry-pi/)
- [How to bind v4l2 USB cameras to the same device names even after reboot?](https://unix.stackexchange.com/questions/77170/how-to-bind-v4l2-usb-cameras-to-the-same-device-names-even-after-reboot)
- [Convert M.2 to PCI-e in VIM3](https://forum.khadas.com/t/pci-e-card-power-supply/12122)
- [WiringPi-Python on VIM](https://docs.khadas.com/zh-cn/vim3/HowToUseWiringPi-Python.html)
- [Change Logo](https://docs.khadas.com/zh-cn/vim3/HowToChangeBootLogo.html)
- [Autostart login tty1 and execute command](https://unix.stackexchange.com/questions/44288/run-gui-application-on-startup)


## Gimbal design and setting 云台设计
Before run SimpleBGC in khadas, please install `librxtx-java`

calibration design

```
|--------------------------|
| Camera & Gimbal Geometry |
|--------------------------|
|  O----> x                |
|  |                       |
| \|/     |--------|       |
|  y      | CAMERA |       |
|         |--------|       |
|                          |
|         |--------| +90   |
|         | GIMBAL | /|\   |
|         |--------|  |    |
|                0<---+yaw |
|--------------------------|
```



## Tracker Design
Color and movement


## ISSUSE & TODO 现存问题
+ offline test: gimbal rotate in preload sequence and saved video
+ add laser power switch in GUI
+ 微弱信号识别及过滤干扰目标: detect moving region
+ send poweroff command to motor after closing  
+ add force exit function, such as reboot?

## Ref 参考
https://superuser.com/questions/497933/50-usb-webcams-in-a-single-computer-is-that-really-possible
