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

sector = 10
readerAuthKey = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

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




if isPi():
    try:
        reader = mfrc522.MFRC522()
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
                            reader.MFRC522_SelectTag(uid)
                            oldData = reader.MFRC522_Read(sector)
                            print(f'Current Sector {sector} data: {str(oldData)}')
#                            newData = list(studentId.to_bytes(4, byteorder='little'))
#                            reader.MFRC522_WriteUltralight(sector, newData)
                            time.sleep(0.1)
                            break
            except ValueError:
                print('Not a valid student id. Failed to associate id')
    except KeyboardInterrupt:
        GPIO.cleanup()
