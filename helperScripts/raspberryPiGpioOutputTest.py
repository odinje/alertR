#!/usr/bin/python

# http://raspberrypiguide.de/howtos/raspberry-pi-gpio-how-to/

import RPi.GPIO as GPIO
import time

# NOTE: this is the actual pin number (not the number of the GPIO)
outputPin = 18


GPIO.setmode(GPIO.BOARD)
GPIO.setup(outputPin, GPIO.OUT)

print "low"
GPIO.output(outputPin, GPIO.LOW)
time.sleep(5)

print "high"
GPIO.output(outputPin, GPIO.HIGH)
time.sleep(5)

print "low"
GPIO.output(outputPin, GPIO.LOW)