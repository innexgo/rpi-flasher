#!/usr/bin/env python3

import os
import sys
import time
import json
import datetime
import requests
import threading

def isPi():
    return sys.implementation._multiarch is 'arm-linux-gnueabihf'

# if raspberry pi
if isPi():
    import RPi.GPIO
    import mfrc522

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

def associateCard(cardId, studentId):
        # There's not a class at the moment
        newCardRequest = requests.get(f'{protocol}://{hostname}/card/new/',
                                        params={'apiKey':apiKey,
                                                'studentId':studentId,
                                                'cardId':cardId})
        if newCardRequest.ok:
            print('Successfully associated card!')
            card = newCardRequest.json()
            print(encounter)
        else:
            print('attempt failed:')
            print(newCardRequest.content)

# Load the config file
with open('innexgo-client.json') as configfile:
    config = json.load(configfile)

    hostname = config['hostname']
    protocol = config['protocol']
    apiKey = config['apiKey']

    if apiKey is None or hostname is None or locationId is None:
        print('error reading the json')
        sys.exit()

    setInterval(updateInfoInfrequent, 1);


    if isPi():
        try:
            reader = mfrc522.MFRC522()
            while True:
                (detectstatus, tagtype) = reader.MFRC522_Request(reader.PICC_REQIDL)
                if detectstatus == reader.MI_OK:
                    (uidstatus, uid) = reader.MFRC522_Anticoll()

                    # TODO add dings
                    if uidstatus == reader.MI_OK:
                        # Convert uid to int
                        cardId = int(bytes(uid).hex(), 16)
                        print(f'logged {cardId}')
                        sendEncounterWithCard(cardId)
                    time.sleep(0.5)
        except KeyboardInterrupt:
            RPi.GPIO.cleanup()
