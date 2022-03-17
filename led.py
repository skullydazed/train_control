from time import sleep_us
from machine import Pin, PWM


class LED:
    """Control the brightness of a single LED.
    """
    def __init__(self, name, pin, frequency=1000):
        self.name = name
        self.pin = Pin(pin, Pin.OUT)
        self.pwm = PWM(self.pin)

        self.pwm.freq(frequency)
        self.pwm.duty_u16(0)

    def __call__(self, brightness, fade_time=2000, fade_steps=100):
        """Change the LED's brightness.
        """
        if brightness < 0 or brightness > 100:
            raise ValueError("Brightness must be between 0 and 100!")

        print('Setting brightness for', self.name, 'to', brightness)

        target = int(brightness / 100 * 65536)

        if target < self.pwm.duty_u16():
            fade_steps = fade_steps * -1

        for i in range(self.pwm.duty_u16(), target, fade_steps):
            self.pwm.duty_u16(i)
            sleep_us(fade_time)

        self.pwm.duty_u16(target)
