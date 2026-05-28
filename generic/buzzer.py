from machine import Pin, PWM
from time import ticks_ms, ticks_diff

class Buzzer:

    def __init__(self, pin, duty=30000, freq=2000, period_on_ms=300, period_off_ms=600):
        self.pwm = PWM(Pin(pin))

        self.duty = duty
        self.freq = freq

        self.period_on_ms = period_on_ms
        self.period_off_ms = period_off_ms

        self.is_beeping = False
        self.state = False

        self.prev_time = 0

    def update(self):

        if not self.state:
            self.pwm.duty_u16(0)
            return

        now = ticks_ms()
        period = self.period_on_ms if self.is_beeping else self.period_off_ms

        if ticks_diff(now, self.prev_time) >= period:
            self.prev_time = now
            self.is_beeping = not self.is_beeping

            if self.is_beeping:
                self.pwm.freq(self.freq)
                self.pwm.duty_u16(self.duty)
            else:
                self.pwm.duty_u16(0)