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
#Funkcja licząca i zwracająca wartość korekcji
def countCorrection():
	global integral
	global last_error
	global lsV
	global csV
	global a1
	global a2
	global b
	a1=15
	a2=201
	b=-13

	#zmienna control informuje nas jak duzy blad nastapil
	control = 0

	#pobranie i normalizacja wartosci wspolczynnikow
	csV = cs.value()
	lsV = a1*ls.value()/a2+b

	#liczenie wartosci bledu
	if csV<lsV:
		error= white - csV
	else:
		error=lsV - white

	#regulator PID
	integral   = 0.5 * integral + error
	derivative = error - last_error
	last_error = error

	#jezeli oba czujniki sa na czarnym korekcja musi byc 0
	if lsV<black and csV<black:
		correction=0
	else:
		#obliczenia korekcji
		correction = int(50 * error + 1 * integral + 1 * derivative)
		control = int(13*error)
		
		#jezeli wsytarczjaco duzy blad ustawiamy duza korekcje 
		#aby w nastepnej fazie algorytm napewno wszedl w algorytm 			#zabezpieczajacy
		if control > 250:
			correction = 1500
		if control < -250:
			correction = -1500
	return int(correction)

#Funkcja licząca współczynniki normalizujacej funkcji liniowej
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

	#pobieranie probek
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

	#liczenie wspolczynnikow
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

	#wyswietlanie wartosci wspolczynnikow na monitorze
	print("a1: %s, a2: %s, b: %s" %(a1, a2, b))
	return w1sum

#Funkcja omijajaca przeszkode
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
	lmotor.run_forever(Przeszkodę omija szybko i speed_sp=2000)
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

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

#Nalezy odkomentowac jezeli kalibrujemy czujniki
#white = calculate()

#wartosci odczytow uzyskiwanych na polu bialym i czarnym
white = 19
black = 9

#zmienne wykorzystywane przez regulator PID
last_error = 0
integral   = 0

#wartosc poczatkowa czujnikow ustawiana na 0
lsV=0
csV=0

while not ts.value():
	#sprawdzamy wartosc czujnika podczerwieni
	if ir.value()<7:
		obstacle()

	#liczenie korekcji i sprawdzanie czy nalezy zalaczyc algorytm zabezpieczajacy
	correction = countCorrection()
	if correction > 1100:
		prvCorrection = 700
		correction = countCorrection()
		while correction>-400:
			lmotor.run_forever(speed_sp=400)
			rmotor.run_forever(speed_sp=-200)
			correction = countCorrection()
	if correction < -1100:
		prvCorrection = -700
		correction = countCorrection()
		while correction<400:
			lmotor.run_forever(speed_sp=-200)
			rmotor.run_forever(speed_sp=400)
			correction = countCorrection()

	#korygowanie pracy silnikow o korekcje
	if abs(correction) < 1100:
		lmotor.run_forever(speed_sp=800+correction)
		rmotor.run_forever(speed_sp=800-correction)
		if correction == 0:
			time.sleep(0.2)
