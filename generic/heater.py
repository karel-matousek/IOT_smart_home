from generic.my_print import my_print
from machine import Pin
import sys
import uselect

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

class Heater:
    def __init__(self, pin=2, hysteresis_dC=1, shared=None):
        self.pin = Pin(pin, Pin.OUT)
        self.state = False
        self.hysteresis_dC = hysteresis_dC
        self.setpoint_dC = 22.0
        self.current_temperature_dC = 0.0
        self.shared = shared

        self.state_update_flag = False
        self.setpoint_update_flag = False

    def calculate_state(self):
        if self.current_temperature_dC < self.setpoint_dC - self.hysteresis_dC and not self.state:
            self.state = True
            self.state_update_flag = True  # Set the flag to indicate that MQTT topic needs to be updated
        elif self.current_temperature_dC > self.setpoint_dC + self.hysteresis_dC and self.state == True:
            self.state = False
            self.state_update_flag = True  # Set the flag to indicate that MQTT topic needs to be updated

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

    def update(self):
        self.pin.value(self.state)  # Turn heater ON