#!/bin/bash
# bash script to start and log mouseGUI for lightDM
# see more at config folder
# by H.F. 20210628

dir="log"
timestamp=$(date '+%Y%m%d-%H%M')
cd /home/khadas/let-there-be-light
/bin/python3 mouseGUI.py > "$dir/out-$timestamp.txt" \
	2> "$dir/err-$timestamp.txt"
