from machine import Pin

class Heater:
    def __init__(self, pin, hysteresis_dC=1, shared=None):
        self.pin = Pin(pin, Pin.OUT)
        self.state = False
        self.hysteresis_dC = hysteresis_dC
        self.setpoint_dC = 22.0
        self.current_temperature_dC = 0.0
        self.shared = shared

    def update(self):
        if self.current_temperature_dC < self.setpoint_dC - self.hysteresis_dC and not self.state:
            self.pin.value(1)  # Turn heater ON
            self.state = True
            self.shared['mqtt_topic_update_flag'] = True  # Set the flag to indicate that MQTT topic needs to be updated
        elif self.current_temperature_dC > self.setpoint_dC + self.hysteresis_dC and self.state == True:
            self.pin.value(0)  # Turn heater OFF
            self.state = False
            self.shared['mqtt_topic_update_flag'] = True  # Set the flag to indicate that MQTT topic needs to be updated