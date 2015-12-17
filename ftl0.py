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
	csV = cs.value()
	lsV = 9*ls.value()/100-15	#na noc
	#lsV=(5*ls.value()/56-13)	#na dzien
	#lsV = 32*ls.value()/197-7692/197
	if csV<lsV:
		error= white - csV
	else:
		error=lsV - white
	integral   = 0.5 * integral + error
	derivative = error - last_error
	last_error = error
	correction = int(60 * error + 1 * integral + 20 * derivative)
	return int(correction)

print("Nasz FTL")
#for x in xrange(10):
white = get_reading('white')
black = get_reading('black')
white = 21
#white = 24
#white = 36

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

last_error = 0
integral   = 0

while not ts.value():
	correction = countCorrection()
	#print("%s, %s" %(error, correction))
	if correction > 1000:
		prvCorrection = 1000
		print("%s" %prvCorrection)
		correction = countCorrection()
		while correction<prvCorrection and correction>-250:
			lmotor.run_forever(speed_sp=500+prvCorrection)
			rmotor.run_forever(speed_sp=500-prvCorrection)
			correction = countCorrection()
	
	if correction < -1000:
		prvCorrection = -1000
		print("%s" %prvCorrection)
		correction = countCorrection()
		while correction>prvCorrection and correction<250:
			lmotor.run_forever(speed_sp=500+prvCorrection)
			rmotor.run_forever(speed_sp=500-prvCorrection)
			correction = countCorrection()
	if abs(correction) < 1000:
		lmotor.run_forever(speed_sp=700+correction)
		rmotor.run_forever(speed_sp=700-correction)

	#time.sleep(0.00001)
