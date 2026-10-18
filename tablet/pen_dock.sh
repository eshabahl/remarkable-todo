#!/bin/sh
# runs on the remarkable. when the pen goes in the dock copy the page to the mac
# and run sync.py there
# start it with: nohup sh pen_dock.sh &
# the dock has a magnet sensor, it shows up as /dev/input/event1 ("Hall effect sensors")

MAC=you@192.168.1.20
NOTEBOOK=7b2e91f4-58c3-4d0a-9e61-2fa8c3d04b17
PAGE=e04c6a2d-913b-4f7e-b5d8-6c1a0f9e3b52
FOLDER=/home/root/.local/share/remarkable/xochitl/$NOTEBOOK

while true; do
    # waits here until the sensor changes (pen in or out)
    # with bs=24 it ran twice every time, 48 works
    dd if=/dev/input/event1 bs=48 count=1 > /dev/null 2>&1
    # evtest exits with 10 if the pen is in the dock
    evtest --query /dev/input/event1 EV_SW SW_PEN_INSERTED
    if [ $? -eq 10 ]; then
        scp $FOLDER/$PAGE.rm $MAC:remarkable-todo/pages/page.rm
        ssh $MAC "cd remarkable-todo && .venv/bin/python sync.py pages/page.rm"
    fi
done
