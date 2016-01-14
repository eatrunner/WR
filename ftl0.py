#!/usr/bin/python
#lewa color_sensor prawa light_sensor

import sys, argparse, time
from ev3dev import *


lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
cs     = color_sensor();        assert cs.connected
ts     = touch_sensor();        assert ts.connected
ls     = light_sensor();        assert ls.connected
ir     = infrared_sensor();     assert ir.connected

cs.mode = 'COL-REFLECT'
ir.mode = 'IR-PROX'

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
	global a1
	global a2
	global b
	a1=18
	a2=196
	b=-17
	control = 0
	csV = cs.value()
	lsV = a1*ls.value()/a2+b
	#print("%s, %s" %(csV, lsV))
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
	if lsV<black and csV<black:
		correction=0
	else:
		correction = int(50 * error + 1 * integral + 1 * derivative)
		control = int(13*error)
		if control > 250:
			correction = 1500
		if control < -250:
			correction = -1500
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

def calculate():
	global a1
	global a2
	global b
	w1 = [0,0,0,0,0,0,0,0,0,0]
	w2 = [0,0,0,0,0,0,0,0,0,0]
	b1 = [0,0,0,0,0,0,0,0,0,0]
	b2 = [0,0,0,0,0,0,0,0,0,0]
	w1sum = 0
	w2sum = 0
	b1sum = 0
	b2sum = 0
	for x in range(10):
		sound.speak("Show me white!", True)
		while not ts.value(): time.sleep(0.1)
		w1[x] = cs.value()
		w2[x] = ls.value()
		print("white.%s: %s, %s" %(x, w1[x], w2[x]))
		sound.speak("OK", True)
		if ts.value():
			exit()
	for y in range(10):
		sound.speak("Show me black!", True)
		while not ts.value(): time.sleep(0.1)
		b1[y] = cs.value()
		b2[y] = ls.value()
		print("black.%s: %s, %s" %(y, b1[y], b2[y]))
		sound.speak("OK", True)
		if ts.value():
			exit()
	for z in range(10):
		w1sum = w1sum + w1[z]
		w2sum = w2sum + w2[z]
		b1sum = b1sum + b1[z]
		b2sum = b2sum + b2[z]
	w1sum = w1sum/10
	w2sum = w2sum/10
	b1sum = b1sum/10
	b2sum = b2sum/10
	a1 = w1sum-b1sum
	a2 = w2sum-b2sum
	b = w1sum-(w2sum*a1/a2)
	print("a1: %s, a2: %s, b: %s" %(a1, a2, b))
	return w1sum

def obstacle():
	global a1
	global a2
	global b
	#stop
	lmotor.run_forever(speed_sp=0)
	rmotor.run_forever(speed_sp=0)
	time.sleep(0.1)
	#turnLeft
	lmotor.run_forever(speed_sp=2000)
	rmotor.run_forever(speed_sp=-500)
	time.sleep(0.3)
	#goForward
	lmotor.run_forever(speed_sp=2000)
	rmotor.run_forever(speed_sp=2000)
	time.sleep(0.5)
	#turnRight
	lmotor.run_forever(speed_sp=0)
	rmotor.run_forever(speed_sp=2000)
	time.sleep(0.4)
	#goForward
	lmotor.run_forever(speed_sp=2000)
	rmotor.run_forever(speed_sp=2000)
	time.sleep(0.9)
	#turnRight
	lmotor.run_forever(speed_sp=0)
	rmotor.run_forever(speed_sp=2000)
	time.sleep(0.5)
	#goForward
	lmotor.run_forever(speed_sp=500)
	rmotor.run_forever(speed_sp=500)
	while (a1*ls.value()/a2+b)>black:
		time.sleep(0.001)
	
	#turnLeft
	lmotor.run_forever(speed_sp=2000)
	rmotor.run_forever(speed_sp=0)
	time.sleep(0.2)

print("Nasz FTL")
#white = calculate()
#17 199 -14
#16 187 -14
#white = get_colors()
#for x in xrange(10):
#white = get_reading('white')
#black = get_reading('black')
white = 21
#white = 24
#white = 36
black = 9

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

last_error = 0
integral   = 0
differ = 0
lsV=0
csV=0
while not ts.value():
	if ir.value()<7:
		obstacle()
	correction = countCorrection()
	#print("%s, %s" %(error, correction))
	if correction > 1100:
		prvCorrection = 700
		#print("%s" %prvCorrection)
		correction = countCorrection()
		while correction>-400:
			lmotor.run_forever(speed_sp=400)
			rmotor.run_forever(speed_sp=-200)
			correction = countCorrection()
	
	if correction < -1100:
		prvCorrection = -700
		#print("%s" %prvCorrection)
		correction = countCorrection()
		while correction<400:
			lmotor.run_forever(speed_sp=-200)
			rmotor.run_forever(speed_sp=400)
			correction = countCorrection()
	if abs(correction) < 1100:
		lmotor.run_forever(speed_sp=500+correction)
		rmotor.run_forever(speed_sp=500-correction)
		if correction == 0:
			time.sleep(0.2)
	

	#time.sleep(0.00001)
