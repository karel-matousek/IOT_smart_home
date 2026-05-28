from generic.my_print import my_print
from machine import Pin
import sys
import uselect
from time import ticks_ms, ticks_diff
from neopixel import NeoPixel
import random

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

class Heater:
    def __init__(self, pin=28, hysteresis_dC=1, shared=None):
        self.pin = Pin(pin, Pin.OUT)
        self.state = False
        self.hysteresis_dC = hysteresis_dC
        self.setpoint_dC = 22.0
        self.current_temperature_dC = 0.0
        self.shared = shared

        self.state_update_flag = False
        self.setpoint_update_flag = False

        self.state_last_upload_time = 0
        self.setpoint_last_upload_time = 0

        self.neopixel_last_update = 0
        self.neopixel_next_delay = 50

        self.np = NeoPixel(Pin(pin), 1)

    def calculate_state(self):
        if self.current_temperature_dC < self.setpoint_dC - self.hysteresis_dC and not self.state:
            self.state = True
            self.state_update_flag = True
            self.state_last_upload_time = ticks_ms()
        elif self.current_temperature_dC > self.setpoint_dC + self.hysteresis_dC and self.state == True:
            self.state = False
            self.state_update_flag = True
            self.state_last_upload_time = ticks_ms()

    def change_setpoint(self):
        # neblokující check
        new_setpoint_dC = 0.0
        if poll.poll(0):
            new_setpoint_dC = sys.stdin.readline().strip()

            try:
                new_setpoint_dC = float(new_setpoint_dC)
            except ValueError:
                my_print("Setpoint must be a valid number")
                return

            if not (10.0 <= new_setpoint_dC <= 40.0):
                my_print("Setpoint must be in the range 10 to 40 °C")
                return

            my_print(f"Changing setpoint to {new_setpoint_dC:.2f} °C")
            self.setpoint_dC = new_setpoint_dC

            self.setpoint_update_flag = True
            self.setpoint_last_upload_time = ticks_ms()

    def update(self):
        if not self.state:
            self.np[0] = (0, 0, 0)
            self.np.write()
            return

        if ticks_diff(ticks_ms(), self.last_update) >= self.next_delay:
            self.last_update = ticks_ms()
            self.next_delay = random.randint(40, 160)

            # Jas plamene
            brightness = random.randint(80, 255)

            # Fire-like barvy
            r = brightness
            g = random.randint(10, brightness // 4)
            b = random.randint(0, 10)

            self.np[0] = (r, g, b)
            self.np.write()