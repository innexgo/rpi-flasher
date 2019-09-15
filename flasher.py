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
    import RPi.GPIO
    import mfrc522
else:
    print('false')

apiKey = None
protocol = None
hostname = None

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
            print('Please touch card...')
            while True:
                (detectstatus, tagtype) = reader.MFRC522_Request(reader.PICC_REQIDL)
                if detectstatus == reader.MI_OK:
                    (uidstatus, uid) = reader.MFRC522_Anticoll()

                    # TODO add dings
                    if uidstatus == reader.MI_OK:
                        # Convert uid to int
                        cardId = int(bytes(uid).hex(), 16)
                        print(f'detected card with id {cardId}')
                        print('input student id')
                        try:
                            studentId = int(input())
                            associateCard(cardId, studentId)
                        except ValueError:
                            print('Not a valid student id. Failed to associate id')
                        print('Please touch card...')
                        time.sleep(0.5)

        except KeyboardInterrupt:
            RPi.GPIO.cleanup()
