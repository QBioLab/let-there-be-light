How to add qt program to lightDM session?

Edit lightdm.conf and mouse.desktop

cat /etc/lightdm/lightdm.conf
[Seat:*]
user-session=mouse
autologin-user=khadas
autologin-user-timeout=delay

cat /usr/share/xsessions/mouse.desktop 
[Desktop Entry]
Name=Mouse-Cancer
Comment=GUI for tracking mouse 
Exec=/home/khadas/let-there-be-light/run.sh
Icon=mouse
Type=Application


ref: https://askubuntu.com/questions/889725/how-can-i-run-my-gui-application-without-desktop-enviroment-and-make-it-fullscre
