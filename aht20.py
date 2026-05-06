import machine
import time

class TMPSensor:
    addr = 0
    i2c_handle = None
    temp = 0
    hum = 0

    def __init__(self, i2c, addr):
        self.i2c_handle = i2c
        self.addr = addr

        time.sleep_ms(100)
        init_data = bytearray([0xbe, 0x08, 0x00])
        self.i2c_handle.writeto(self.addr, init_data)
        time.sleep_ms(10)

    def measure(self):
        trigger_data = bytearray([0xac, 0x33, 0x00])
        self.i2c_handle.writeto(self.addr, trigger_data)
        time.sleep_ms(100)

        data = self.i2c_handle.readfrom(self.addr, 7)
        #print(data)

        # HUMIDITY
        humidity_value = (data[1] << 12) | (data[2] << 4) | ((data[3] & 0b11110000) >> 4)
        #print(humidity)

        humidity = (humidity_value / 2**20) * 100
        #print(humidity)

        self.hum = humidity

        # TEMPERATURE
        temperature_value = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        temperature = (temperature_value / 2**20) * 200-50
        self.temp = temperature
