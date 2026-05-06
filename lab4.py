import machine
import time
import aht20
import os

DEVICE_ADDR = 56
period = 3000
led7 = machine.Pin(7, machine.Pin.OUT, value=0)
led9 = machine.Pin(9, machine.Pin.OUT, value=0)
led8 = machine.Pin(8, machine.Pin.OUT, value=0)

i2c_handle = machine.I2C(0, scl = 1, sda = 0, freq = 100000)
#print(i2c_handle.scan())

sensor = aht20.TMPSensor(i2c_handle, DEVICE_ADDR)
sensor.measure()

"""
f = open('/sd/update.py', 'r')
f_dest = open('/novyfw.py', 'w')
data = f.read()
f_dest.write(data)
f_dest.close()

f.close()"""

#import novyfw

while(1):
    sensor.measure()
    print(sensor.hum)
    print(sensor.temp)

    if sensor.temp > 24:
        led9.value(1)
    else:
        led9.value(0)

    if sensor.hum > 60:
        led8.value(1)
    else:
        led8.value(0)

    time.sleep_ms(2000)
