#!/usr/bin/env python3

import os
import sys
import time
import json
import getpass
import datetime
import requests
import readline
import threading

def isPi():
    return sys.implementation._multiarch == 'arm-linux-gnueabihf'

# if raspberry pi
if isPi():
    import RPi.GPIO as GPIO
    import altered_mfrc522
else:
    print('not a pi lmao')

apiKey = None
protocol = None
hostname = None

sector = 10

def beep(hertz, duration):

    # Set up soundPins for buzzer
    if not soundInitialized:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(soundPin, GPIO.OUT)
    soundChannel = GPIO.PWM(soundPin, hertz)
    soundChannel.start(50.0)
    time.sleep(duration)
    soundChannel.stop()


def beepUp():
    beep(1000, 0.1)
    beep(2000, 0.1)


def beepDown():
    beep(2000, 0.1)
    beep(1000, 0.1)

def beepFlat():
    beep(2000, 0.2)

def beepError():
    beep(1000, 0.1)
    time.sleep(0.05)
    beep(1000, 0.1)
    time.sleep(0.05)
    beep(1000, 0.1)

def beepNetError():
    for i in range(0, 4):
        beep(1000, 0.01)
        time.sleep(0.05)

def currentMillis():
    return round(1000 * time.time())

def printMillis(millis):
    print(datetime.datetime.fromtimestamp(millis/1000.0))

if isPi():
    try:
        reader = altered_mfrc522.MFRC522()
        while True:
            try:
                # First grab student id
                print('\n\n=============== BEGIN CARD FLASHING PROCESS ===============')
                print('Please enter student ID...')
                studentId = int(input())
                print('\nPlease touch card...')
                while True:
                    (detectstatus, tagtype) = reader.MFRC522_Request(reader.PICC_REQIDL)
                    if detectstatus == reader.MI_OK:
                        (uidstatus, uid) = reader.MFRC522_Anticoll()
                        if uidstatus == reader.MI_OK:
                            # Select this tag
                            reader.MFRC522_SelectTag(uid)
                            
                            # Print current data on card
                            print(f'Writing to sector {sector}')
                            print(f'Current: {reader.MFRC522_Read(sector)}')

                            # Get data and write it to the card
                            writeStatus = reader.MFRC522_WriteUltralight(sector, 
                                    list(studentId.to_bytes(4, byteorder='little')))

                            # Print current data on card
                            print(f'After write: {reader.MFRC522_Read(sector)}')
                            print('(These should be different)')

                            time.sleep(0.1)
                            break
            except ValueError:
                print('Not a valid student id. Failed to associate id')
    except KeyboardInterrupt:
        GPIO.cleanup()
