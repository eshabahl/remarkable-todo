#!/bin/sh
# runs on the remarkable. when the pen goes in the dock copy the page to the mac
# the dock has a magnet sensor, it shows up as /dev/input/event1 ("Hall effect sensors")

MAC=you@192.168.1.20
NOTEBOOK=7b2e91f4-58c3-4d0a-9e61-2fa8c3d04b17
PAGE=e04c6a2d-913b-4f7e-b5d8-6c1a0f9e3b52
FOLDER=/home/root/.local/share/remarkable/xochitl/$NOTEBOOK

while true; do
    # waits here until the sensor changes
    dd if=/dev/input/event1 bs=24 count=1 > /dev/null 2>&1
    scp $FOLDER/$PAGE.rm $MAC:remarkable-todo/pages/page.rm
done
