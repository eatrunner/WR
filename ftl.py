#!/usr/bin/python

import sys, argparse, time
from ev3dev import *


lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
cs     = color_sensor();        assert cs.connected
ts     = touch_sensor();        assert ts.connected

cs.mode = 'COL-REFLECT'

def get_reading(color):
    sound.speak("Show me %s!" % color, True)
    while not ts.value(): time.sleep(0.1)

    v = cs.value()
    print("%s: %s" %(color, v))
    sound.speak("OK", True)
    return v

print("Nasz FTL")
white = get_reading('white')
black = get_reading('black')
mid   = 0.5 * (white + black)

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'

last_error = 0
integral   = 0

while not ts.value():
    error      = mid - cs.value()
    integral   = 0.5 * integral + error
    derivative = error - last_error
    last_error = error

    correction = int(3.0 * error)# + 0.5 * integral + 2.0 * derivative)

    lmotor.run_forever(speed_sp=500+correction)
    rmotor.run_forever(speed_sp=500-correction)

    time.sleep(0.01)
