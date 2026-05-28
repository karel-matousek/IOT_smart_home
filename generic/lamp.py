from machine import Pin

class Lamp:
    def __init__(self, pin="LED"):
        self.pin = Pin(pin, Pin.OUT)
        self.state = False

    def update(self):
        self.pin.value(self.state)