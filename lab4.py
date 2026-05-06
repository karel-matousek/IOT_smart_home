import machine
import time
import aht20
from generic.wifi import initialize_wifi
from generic import config
from generic.umqtt import implementation as mqtt
from generic.my_print import my_print

DEVICE_ADDR = 56
period = 3000

# LEDs
led7 = machine.Pin(7, machine.Pin.OUT, value=0)
led9 = machine.Pin(9, machine.Pin.OUT, value=0)
led8 = machine.Pin(8, machine.Pin.OUT, value=0)

# Buttons
gpio20 = machine.Pin(20, machine.Pin.IN) # Pin.IN?
gpio21 = machine.Pin(21, machine.Pin.IN)

i2c_handle = machine.I2C(0, scl = 1, sda = 0, freq = 100000)
#print(i2c_handle.scan())

sensor = aht20.TMPSensor(i2c_handle, DEVICE_ADDR)
sensor.measure()

while(1):
    sensor.measure()
    print(sensor.hum)
    print(sensor.temp)

    # Switch Heating ON
    if sensor.temp > 24:
        led9.value(1)
    # Switch Heating OFF
    else:
        led9.value(0)

    
    if sensor.hum > 60:
        led8.value(1)
    else:
        led8.value(0)
        

    time.sleep_ms(5000)
