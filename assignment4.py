#!/usr/bin/python
# Assignment 4 #

### import Python Modules ###
import threading
import RPi.GPIO as GPIO
import time 	# for time delay and threshold

### Pin Numbering Declaration (setup channel mode of the Pi to Board values) ###
LED_R = 6
LED_G = 5
LED_B = 13
LED_Y = 12
BTN_R = 18
BTN_G = 25
BTN_B = 22
BTN_Y = 27
period = 1 #default period is 1 second
pin = False
GPIO.setwarnings(False)		#to disable warnings


### Set GPIO pins (for inputs and outputs) and all setups needed based on assingment description ###
GPIO.setmode(GPIO.BCM) #using GPIO number instead of pin number
GPIO.setup(LED_R, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(LED_G, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(LED_B, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(LED_Y, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(BTN_R, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BTN_G, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BTN_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BTN_Y, GPIO.IN, pull_up_down = GPIO.PUD_UP)


while True:
	GPIO.output(LED_R, not GPIO.input(BTN_R)) # if red button pressed, turn on red LED
	GPIO.output(LED_G, not GPIO.input(BTN_G)) # if green button pressed, turn on green LED
	GPIO.output(LED_B, not GPIO.input(BTN_B)) # if blue button pressed, turn on blue LED
	GPIO.output(LED_Y, not GPIO.input(BTN_Y)) # if yellow button pressed, turn on yellow LED
	time.sleep(.1) #stay on on for .1 seconds
	# turn off all LEDs
	GPIO.output(LED_R, False) 
	GPIO.output(LED_G, False)
	GPIO.output(LED_B, False)
	GPIO.output(LED_Y, False)

	if ((not GPIO.input(BTN_G)) and (period > 0)): # if green is pressed, period gets cut in half
		period = period/2
		print("Blinking period is now: " + str(period)) # display current period
	if (not GPIO.input(BTN_R)): # if red button is pressed, period doubles
		period = period*2
		print("Blinking period is now: " + str(period)) # display current period
	# when yellow and blue pressed simultaneously, enter blink mode
	if ((not GPIO.input(BTN_B)) and (not GPIO.input(BTN_Y))):
		print ("Blinking.. ")
		timer = time.time() + 10 # turn off blinking after 10 seconds
		time.sleep(0.5) #delay for 0.5 seoonds to allow for detection of second time
		while (time.time() < timer): # repeat blinking for 10 seconds
			if((not GPIO.input(BTN_B)) and (not GPIO.input(BTN_Y))): #detecting stop signal
				print ("Blinking halted..")
				timer = 0 # exit while loop by changing condition
			else:   # blink the LEDs for 10 seconds or until blue and yellow buttons are pressed again
				GPIO.output(LED_R, True)
				GPIO.output(LED_G, True)
				GPIO.output(LED_B, True)
				GPIO.output(LED_Y, True)
				time.sleep(period)
				GPIO.output(LED_R, False)
				GPIO.output(LED_G, False)
				GPIO.output(LED_B, False)
				GPIO.output(LED_Y, False)
				time.sleep(period)
