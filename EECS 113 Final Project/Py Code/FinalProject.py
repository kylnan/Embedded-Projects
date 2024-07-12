#!/usr/bin/env python3
########################################################################
# Filename    : FinalProject.py
# Description : Building Management System
# author      : Kyle Zyler Cayanan
# modification: 2022/06/06
########################################################################
import json
import threading
import time
from datetime import date

import RPi.GPIO as GPIO
import requests

# LCD and DHT Libraries
# files can be found in parent directory for project
import Freenove_DHT as DHT
from Adafruit_LCD1602 import Adafruit_CharLCD
from PCF8574 import PCF8574_GPIO

DHTPin = 27  # define DHT pin
IR_ledPin = 18  # define IR led pin
IR_sensorPin = 17  # define IR sensor pin

HVAC_buttonPin = 6  # define HVAC button pin
heater_buttonPin = 13  # define heater button pin
door_buttonPin = 5  # deine door button pin

HVAC_ledPin = 12  # define HVAC led pin
heater_ledPin = 24  # define heater led pin

# threading mutex variable
lcdLock = threading.Lock()

# initial GPIO
GPIO.setmode(GPIO.BCM)  # use GPIO numbering
GPIO.setwarnings(False)

PCF8574_address = 0x27  # I2C address of the PCF8574 chip
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip

# Create PCF8574 GPIO adapter
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print(" I2C adress Error !")
        exit(1)

# Create LCD, passing in MCP GPIO adapter
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)


def setup():
    GPIO.setup(IR_ledPin, GPIO.OUT, initial=GPIO.LOW)  # set IR ledPin to OUTPUT mode
    GPIO.setup(IR_sensorPin, GPIO.IN)  # set IR sensorPin to INPUT mode

    GPIO.setup(HVAC_buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set HVAC buttonPin to INPUT mode
    GPIO.setup(heater_buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set heater buttonPin to INPUT mode
    GPIO.setup(door_buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set door buttonPin to INPUT mode
    GPIO.setup(HVAC_ledPin, GPIO.OUT, initial=GPIO.LOW)  # set HVAC ledPin to OUTPUT mode
    GPIO.setup(heater_ledPin, GPIO.OUT, initial=GPIO.LOW)  # set heater ledPin to OUTPUT mode


def destroy():
    # lcd
    lcd.clear()

    # ambient lighting
    GPIO.output(IR_ledPin, False)

    # HVAC
    GPIO.output(HVAC_ledPin, False)
    GPIO.output(heater_ledPin, False)

    # for all
    GPIO.cleanup()


def hvacSystem():
    humidity = int(cimisData())
    dht = DHT.DHT(DHTPin)
    read = dht.readDHT11()
    temp = int(dht.temperature * (9 / 5) + 32)
    weather = int(temp + 0.05 * humidity)
    setTemp = weather
    lcdLock.acquire()
    lcd.setCursor(0, 0)
    lcd.message('' + str(weather) + '/' + str(setTemp))
    lcd.setCursor(0, 1)
    lcd.message('H: OFF')
    lcdLock.release()
    tempList = []
    tempList.append(temp)
    tempavg = int(temp)

    while True:
        # calculate temperature every second and avg last 3 measurements, calculating weather index
        time.sleep(1)
        read = dht.readDHT11()
        temp = int(dht.temperature * (9 / 5) + 32)
        tempList.append(temp)
        if len(tempList) > 3:
            tempList.pop(0)
        if len(tempList) > 2:
            tempavg = int((tempList[0] + tempList[1] + tempList[2]) / 3)
        weather = int(tempavg + 0.05 * humidity)
        lcdLock.acquire()
        lcd.setCursor(0, 0)
        lcd.message('' + str(weather) + '/' + str(setTemp))
        lcdLock.release()

        if not GPIO.input(HVAC_buttonPin):
            print('Temp lowered\n')
            setTemp -= 1
            lcdLock.acquire()
            lcd.setCursor(0, 0)
            lcd.message('' + str(weather) + '/' + str(setTemp))
            lcdLock.release()
        if not GPIO.input(heater_buttonPin):
            print('Temp increased\n')
            setTemp += 1
            lcdLock.acquire()
            lcd.setCursor(0, 0)
            lcd.message('' + str(weather) + '/' + str(setTemp))
            lcdLock.release()

        if setTemp >= (weather + 3) and GPIO.input(door_buttonPin):
            GPIO.output(HVAC_ledPin, False)
            GPIO.output(heater_ledPin, True)
            lcdLock.acquire()
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.message('HEAT TURNED ON')
            time.sleep(3)
            lcd.clear()
            lcdLock.release()
            while setTemp >= (weather + 3) and GPIO.input(door_buttonPin):
                if (not GPIO.input(HVAC_buttonPin)) or (not GPIO.input(heater_buttonPin)):
                    break
                lcdLock.acquire()
                lcd.setCursor(0, 1)
                lcd.message('H:HEAT')
                lcd.setCursor(0, 0)
                lcd.message('' + str(weather) + '/' + str(setTemp))
                lcdLock.release()
        if (setTemp < (weather + 3)) and (setTemp > (weather - 3)):
            GPIO.output(HVAC_ledPin, False)
            GPIO.output(heater_ledPin, False)
            lcdLock.acquire()
            lcd.setCursor(0, 1)
            lcd.message('H: OFF')
            lcdLock.release()
        if setTemp <= (weather - 3) and GPIO.input(HVAC_buttonPin):
            GPIO.output(HVAC_ledPin, True)
            GPIO.output(heater_ledPin, False)
            lcdLock.acquire()
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.message('AC ON')
            time.sleep(3)
            lcd.clear()
            lcdLock.release()
            while setTemp <= (weather - 3) and GPIO.input(door_buttonPin):
                if (not GPIO.input(HVAC_buttonPin)) or (not GPIO.input(heater_buttonPin)):
                    break
                lcdLock.acquire()
                lcd.setCursor(0, 1)
                lcd.message('H:COOL')
                lcd.setCursor(0, 0)
                lcd.message('' + str(weather) + '/' + str(setTemp))
                lcdLock.release()


def ambientLighting():  # Motion detector sensing for lighting
    while True:
        if GPIO.input(IR_sensorPin) == GPIO.HIGH:
            GPIO.output(IR_ledPin, GPIO.input(IR_sensorPin))
            lcdLock.acquire()
            lcd.setCursor(11, 1)
            lcd.message('L: ON')
            lcdLock.release()
            time.sleep(10)
            GPIO.output(IR_ledPin, False)
        else:
            GPIO.output(IR_ledPin, GPIO.LOW)
            lcdLock.acquire()
            lcd.setCursor(11, 1)
            lcd.message('L:OFF')
            lcdLock.release()


def doorSecurity():  # security system/hvac control
    while True:
        if not GPIO.input(door_buttonPin):
            GPIO.output(HVAC_ledPin, False)
            GPIO.output(heater_ledPin, False)
            lcdLock.acquire()
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.message("Door/WINDOW OPEN \n HVAC HALTED")
            time.sleep(3)
            lcd.clear()
            lcdLock.release()
            while not GPIO.input(door_buttonPin):
                GPIO.output(HVAC_ledPin, False)
                GPIO.output(heater_ledPin, False)
                lcdLock.acquire()
                lcd.setCursor(8, 0)
                lcd.message("D/W: OPEN")
                lcd.setCursor(0, 1)
                lcdLock.release()
        else:
            lcdLock.acquire()
            lcd.setCursor(8, 0)
            lcd.message("D/W:SAFE")
            lcdLock.release()


def cimisData():
    # Get most recent humidity value from CIMIS
    today = date.today()
    dateStamp = today.strftime("%Y-%m-%d")

    parameters = {
        "appKey": "fa3d0d05-8375-49a2-b53a-f764ec9817ce",
        "targets": "92602",
        "startDate": dateStamp,
        "endDate": dateStamp,
        "unitOfMeasure": "M",
        "dataItems": "hly-rel-hum"
    }
    url = "https://et.water.ca.gov/api/data"
    response = requests.get(url, params=parameters)

    #  parsing the data from the json file and assigning corresponding data
    jsonHumidityLoaded = json.loads(response.content)['Data']['Providers'][0]['Records']

    for x in range(len(jsonHumidityLoaded)):
        if jsonHumidityLoaded[len(jsonHumidityLoaded) - x - 1]['HlyRelHum']['Value'] is not None:
            humidity = jsonHumidityLoaded[len(jsonHumidityLoaded) - x - 1]['HlyRelHum']['Value']
            break
        else:
            continue
        break

    return humidity


if __name__ == '__main__':
    print('Welcome to the Building Management System! ')
    # GPIO Setup
    setup()
    mcp.output(3, 1) # enable backlight on the LCD
    lcd.begin(16, 2) # set columns/rows on the LCD

    hvacThread = threading.Thread(target=hvacSystem)
    # hvacThread.daemon = True
    ambientThread = threading.Thread(target=ambientLighting)
    # ambientThread.daemon = True
    securityThread = threading.Thread(target=doorSecurity)
    # securityThread.daemon = True

    try:
        ambientThread.start()
        hvacThread.start()
        securityThread.start()

    except KeyboardInterrupt:
        destroy()
