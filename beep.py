#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)

pin = 14

GPIO.setup(pin,GPIO.OUT)
p = GPIO.PWM(pin,1190)
p.start(50.0)

input("Press Enter key to Stop 1kHz PWM @ 50% duty cycle")

GPIO.cleanup()
