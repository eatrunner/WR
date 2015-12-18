#!/usr/bin/python
#lewa color_sensor prawa light_sensor

import sys, argparse, time
from ev3dev import *


lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
cs     = color_sensor();        assert cs.connected
ts     = touch_sensor();        assert ts.connected
ls     = light_sensor();        assert ls.connected

cs.mode = 'COL-REFLECT'

def get_reading(color):
	sound.speak("Show me %s!" % color, True)
	while not ts.value(): time.sleep(0.1)
	v = cs.value()
	v1 = 9*ls.value()/100-15	#na noc
	#v1 = (5*ls.value()/56-13)	#na dzien
	#v1 = 32*ls.value()/197-7692/197
	print("%s: %s, %s" %(color, v, v1))
	sound.speak("OK", True)
	return v

def countCorrection():
	global integral
	global last_error
	global differ
	global lsV
	global csV
	csV = cs.value()
	lsV = a1*ls.value()/a2+b
	#lsV = a*ls.value()+b
	#lsV = 9*ls.value()/100-15	#na noc
	#lsV=(5*ls.value()/56-13)	#na dzien
	#lsV = 32*ls.value()/197-7692/197
	differ = lsV - csV
	if csV<lsV:
		error= white - csV
	else:
		error=lsV - white
	integral   = 0.5 * integral + error
	derivative = error - last_error
	last_error = error
	correction = int(60 * error + 1 * integral + 5 * derivative)
	return int(correction)

def get_colors():
	#global a
	global a1
	global a2
	global b
	sound.speak("Show me white!", True)
	while not ts.value(): time.sleep(0.1)
	w1 = cs.value()
	w2 = ls.value()
	print("white: %s, %s" %(w1, w2))
	sound.speak("OK", True)
	sound.speak("Show me black!", True)
	while not ts.value(): time.sleep(0.1)
	b1 = cs.value()
	b2 = ls.value()
	print("black: %s, %s" %(b1, b2))
	sound.speak("OK", True)
	a1 = w1-b1
	a2 = w2-b2
	#a = (w1-b1)/(w2-b2)
	b = w1-(w2*a1/a2)
	#print("calculated white: %s, %s" %(w1, w2*a+b))
	#print("calculated black: %s, %s" %(b1, b2*a+b))
	#print("a: %s, b: %s" %(a, b))
	print("calculated white: %s, %s" %(w1, w2*a1/a2+b))
	print("calculated black: %s, %s" %(b1, b2*a1/a2+b))
	print("a1: %s, a2: %s, b: %s" %(a1, a2, b))
	return w1

print("Nasz FTL")
white = get_colors()
#for x in xrange(10):
#white = get_reading('white')
#black = get_reading('black')
#white = 21
#white = 24
#white = 36

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

last_error = 0
integral   = 0
differ = 0
lsV=0
csV=0
while not ts.value():
	correction = countCorrection()
	#print("%s, %s" %(error, correction))
	if lsV<10:
		prvCorrection = 700
		#print("%s" %prvCorrection)
		correction = countCorrection()
		while correction<1000 and correction>-400:
			lmotor.run_forever(speed_sp=300)
			rmotor.run_forever(speed_sp=-100)
			correction = countCorrection()
	
	if csV<10:
		prvCorrection = -700
		#print("%s" %prvCorrection)
		correction = countCorrection()
		while correction>-1000 and correction<400:
			lmotor.run_forever(speed_sp=-100)
			rmotor.run_forever(speed_sp=300)
			correction = countCorrection()
	if abs(correction) < 1000:
		lmotor.run_forever(speed_sp=700+correction)
		rmotor.run_forever(speed_sp=700-correction)

	#time.sleep(0.00001)
