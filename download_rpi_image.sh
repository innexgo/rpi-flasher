#!/bin/sh
aria2c -x 4 -d /tmp/ --lowest-speed-limit=20K -o raspbian_lite_latest https://downloads.raspberrypi.org/raspbian_lite_latest
