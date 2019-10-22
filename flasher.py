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
    import mfrc522
else:
    print('not a pi lmao')


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

# Attempts to associate card, returns card if succeeded, error if failed
def associateCard(cardId, studentId):
        try:
            # There's not a class at the moment
            newCardRequest = requests.get(f'{protocol}://{hostname}/api/card/new/',
                                params={'apiKey':apiKey,
                                        'studentId':studentId,
                                        'cardId':cardId})
            if newCardRequest.ok:
                print('Successfully associated card!')
                card = newCardRequest.json()
                return card
            else:
                print(f'Could not associate card: HTTP Error {newCardRequest.status_code}')
                return None
        except requests.exceptions.RequestException:
            print(f'Failed to connect to {protocol}://{hostname}')

# Attempts to get key, returns key if succeeeded, error if failed
def getKey():
    while True:
        print(f'Please enter email to login into {hostname}:')
        email = input()
        print(f'Please enter password to login into {hostname}:')
        password = getpass.getpass()
        try:
            getApiKeyRequest = requests.get(f'{protocol}://{hostname}/api/apiKey/new/',
                                        params={'email':email,
                                                'password':password,
                                                'expirationTime':currentMillis()+30*60*1000})
            if getApiKeyRequest.ok:
                print('Successfully logged in!')
                return getApiKeyRequest.json()['key']
            else:
                print(f'Could not associate card: HTTP Error {getApiKeyRequest.status_code}')
        except:
            print(f'Failed to connect to {protocol}://{hostname}')
            sys.exit(1)





# Load the config file
with open('/boot/innexgo-flasher.json') as configfile:
    config = json.load(configfile)

    hostname = config['hostname']
    protocol = config['protocol']

    if hostname is None or protocol is None:
        print('error reading the json')
        sys.exit()

    apiKey = getKey()

    if isPi():
        try:
            reader = mfrc522.MFRC522()
            while True:
                try:
                    # First grab student id
                    print('Please enter student ID...')
                    studentId = int(input())
                    print('\nPlease touch card...')
                    while True:
                        (detectstatus, tagtype) = reader.MFRC522_Request(reader.PICC_REQIDL)
                        if detectstatus == reader.MI_OK:
                            (uidstatus, uid) = reader.MFRC522_Anticoll()
                            # TODO add dings
                            if uidstatus == reader.MI_OK:
                                # Convert uid to int
                                cardId = int(bytes(uid).hex(), 16)
                                print(f'detected card with id {cardId}')
                                associateCard(cardId, studentId)
                                time.sleep(0.5)
                                break;
                except ValueError:
                    print('Not a valid student id. Failed to associate id')
        except KeyboardInterrupt:
            GPIO.cleanup()
