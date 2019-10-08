#!/usr/bin/env python3

import os
import sys
import time
import json
import datetime
import requests
import readline
import threading

def isPi():
    return sys.implementation._multiarch == 'arm-linux-gnueabihf'

# if raspberry pi
if isPi():
    import RPi.GPIO as GPIO
    import mfrc522
else:
    print('not a pi lmao')

# This is the default key for authentication
rfidKey = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

apiKey = None
protocol = None
hostname = None

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

# setInterval for python
def setInterval(func, sec):
    def func_wrapper():
        setInterval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

# Attempts to associate card
def associateCard(cardId, studentId):
        try:
            # There's not a class at the moment
            newCardRequest = requests.get(f'{protocol}://{hostname}/card/new/',
                                params={'apiKey':apiKey,
                                        'studentId':studentId,
                                        'cardId':cardId})
            if newCardRequest.ok:
                print('Successfully associated card!')
                card = newCardRequest.json()
            else:
                print(f'attempt failed: {newCardRequest.status_code}')
                print(newCardRequest.content)
        except requests.exceptions.RequestException:
            print(f'Failed to connect to {protocol}://{hostname}')

# Load the config file
with open('innexgo-flasher.json') as configfile:
    config = json.load(configfile)

    hostname = config['hostname']
    protocol = config['protocol']
    apiKey = config['apiKey']

    if hostname is None or protocol is None or apiKey is None:
        print('error reading the json')
        sys.exit()

    if isPi():
        try:
            reader = mfrc522.MFRC522()
            while True:
                try:
                    # First grab student id
                    print('Please enter student ID...')
                    studentId = int(input())
                    print('Please touch card...')
                    (detectstatus, tagtype) = reader.MFRC522_Request(reader.PICC_REQIDL)
                    if detectstatus == reader.MI_OK:
                        (uidstatus, uid) = reader.MFRC522_Anticoll()
                        # TODO add dings
                        if uidstatus == reader.MI_OK:
                            # Convert uid to int
                            cardId = int(bytes(uid).hex(), 16)
                            print(f'detected card with id {cardId}')
                            associateCard(cardId, studentId)


                            # Select the scanned tag
                            MIFAREReader.MFRC522_SelectTag(uid)
                            # Authenticate us
                            authStatus = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, 8, rfidKey, uid)
                            if authStatus == reader.MI_OK:
                                print('successfully authenticated to card, beginning write');
                                # Now we must write the student id for the card
                                reader.MFRC522_Write(1, uid.to_bytes(4, byteorder='big'))
                                reader.MFRC522_StopCrypto1()
                            else:
                                print('failed to authenticate to card! (still usable though)')
                            time.sleep(0.5)
                except ValueError:
                    print('Not a valid student id. Failed to associate id')
        except KeyboardInterrupt:
            RPi.GPIO.cleanup()
