from machine import Pin, PWM


class Train:
    """A class for controlling DC Trains using an H-bridge (L298N or similar).

    Args:
        enable: The speed control (enable) pin on the H-bridge
        in1: The first direction control pin
        in2: The second direction control pin
    """
    STOPPED = 1
    FORWARD = 2
    BACKWARD = 3

    def __init__(self, name, enable, in1, in2, min_speed=0, max_speed=65536, pwm_frequency=50):
        self.name = name
        self.enable = PWM(Pin(enable, Pin.OUT))
        self.in1 = Pin(in1, Pin.OUT)
        self.in2 = Pin(in2, Pin.OUT)
        self._speed = 0
        self.min_speed = min_speed
        self.max_speed = max_speed

        self.enable.freq(pwm_frequency)
        self.enable.duty_u16(self.min_speed)
        self.in1.value(0)
        self.in2.value(0)

    @property
    def direction(self):
        """Returns one of the TrainDirection enums.
        """
        if self.in1.value() == 0 and self.in2.value() == 1:
            return self.FORWARD

        elif self.in1.value() == 1 and self.in2.value() == 0:
            return self.BACKWARD

        return self.STOPPED

    @direction.setter
    def direction(self, value):
        if value == self.FORWARD:
            self.in1.value(0)
            self.in2.value(1)
        elif value == self.BACKWARD:
            self.in1.value(1)
            self.in2.value(0)
        elif value == self.STOPPED:
            self.in1.value(0)
            self.in2.value(0)
        else:
            raise ValueError(f"{value} is an unknown direction.")

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value > self.max_speed:
            raise ValueError(f"Max speed is {self.max_speed}!")

        if value < self.min_speed:
            raise ValueError(f"Min speed is {self.min_speed}!")

        self._speed = value
        print('Train', self.name, 'set to speed', self._speed)

    def backward(self):
        """Have the train move backward at the current speed.
        """
        self.direction = self.BACKWARD
        print('Train', self.name, 'direction set to backward.')

    def forward(self):
        """Have the train move forward at the current speed.
        """
        self.direction = self.FORWARD
        print('Train', self.name, 'direction set to forward.')

    def stop(self):
        """Stop the train gradualy.

        FIXME: Currently stops immediately
        """
        self.direction = self.STOPPED
        print('Train', self.name, 'stopped.')

    def estop(self):
        """Stop the train immediately.
        """
        self.direction = self.STOPPED
        print('Train', self.name, 'stopped.')
