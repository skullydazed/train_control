"""Train Control - The brain of my model train.

Pins:
    GP0     I2S-BCK
    GP1     I2S-LRCK
    GP2     I2S-DIN
    GP3     RLY-IN3
    GP4     BUTTON1
    GP5     LED1
    GP6     VFD-ENABLE
    GP7     VFD-RS
    GP8     TRAIN1A
    GP9     TRAIN1B
    GP10    TRAIN2A
    GP11    TRAIN2B
    GP12    LED2
    GP13    LED3
    GP14    BUTTON2
    GP15    BUTTON3
    GP16    IR-DETECT1
    GP17    IR-DETECT2
    GP18    IR-DETECT3
    GP19    IR-DETECT4
    GP20    VFD-DB4
    GP21    VFD-DB5
    GP22    VFD-DB6
    GP26    VFD-DB7
    GP27    RLY-IN2
    GP28    RLY-IN1
"""
import utime
from machine import Pin, PWM

MAIN_LOOP_TIME = 0.005


class TrainDirection:
    STOPPED = 1
    FORWARD = 2
    BACKWARD = 3


class LED:
    """Control the brightness of a single LED.
    """
    def __init__(self, pin, frequency=1000):
        self.pin = Pin(pin, Pin.OUT)
        self.pwm = PWM(self.pin)

        self.pwm.freq(frequency)
        self.pwm.duty_u16(0)

    def __call__(self, brightness, fade_time=0.002, fade_steps=100):
        """Change the LED's brightness.
        """
        if brightness < 0 or brightness > 100:
            raise ValueError("Brightness must be between 0 and 100!")

        target = int(brightness / 100 * 65536)

        if target < self.pwm.duty_u16():
            fade_steps = fade_steps * -1

        for i in range(self.pwm.duty_u16(), target, fade_steps):
            print('Duty, hehehehe', i)
            self.pwm.duty_u16(i)
            utime.sleep(fade_time)

        self.pwm.duty_u16(target)


class TrainTrack:
    """A class for controlling DC Trains using an H-bridge (L298N or similar).

    Args:
        enable: The speed control (enable) pin on the H-bridge
        in1: The first direction control pin
        in2: The second direction control pin
    """
    def __init__(self, enable, in1, in2, min_speed=0, max_speed=65536, pwm_frequency=50):
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
            return TrainDirection.FORWARD

        elif self.in1.value() == 1 and self.in2.value() == 0:
            return TrainDirection.BACKWARD

        return TrainDirection.STOPPED

    @direction.setter
    def direction(self, value):
        if value == TrainDirection.FORWARD:
            self.in1.value(0)
            self.in2.value(1)
        elif value == TrainDirection.BACKWARD:
            self.in1.value(1)
            self.in2.value(0)
        elif value == TrainDirection.STOPPED:
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

    def backward(self):
        """Have the train move forward at the current speed.
        """
        return self.direction(TrainDirection.BACKWARD)

    def forward(self):
        """Have the train move forward at the current speed.
        """
        return self.direction(TrainDirection.FORWARD)

    def stop(self):
        """Have the train move forward at the current speed.
        """
        return self.direction(TrainDirection.STOPPED)



class IRSensor:
    def __init__(self, name, pin):
        self.name = name
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)

    def __call__(self):
        return self.pin.value()


class Button:
    def __init__(self, name, pin, debounce_time=MAIN_LOOP_TIME):
        self.debounce_time = debounce_time
        self.name = name
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.last_value = self.new_value = self.pin.value()

    def __call__(self):
        """Returns True if the button has been pressed.

        For debouncing purposes the first state change is ignored.
        """
        current_value = self.pin.value()
        has_changed = False

        if self.last_value != self.new_value: 
            if self.new_value == current_value:
                self.last_value = current_value
                has_changed = True
        elif self.last_value != current_value:
            self.new_value = current_value

        return self.last_value == 0, has_changed


class SceneControl:
    def __init__(self):
        self.smoke = Pin(28, Pin.OUT)
        self.pi_led = LED(25)

        # Push buttons
        self.buttons = [
            Button('Button1', 4), 
            Button('Button2', 14), 
            Button('Button3', 15),
        ]

        # IR Sensors to detect train position
        self.ir_sensors = [
            Button('IR1', 16),
            Button('IR2', 17),
            Button('IR3', 18),
            Button('IR4', 19),
        ]

        # Devices that need names
        self.LED1 = LED(7)
        self.LED2 = LED(12)
        self.LED3 = LED(13)

        self.RELAY2 = Pin(27, Pin.OUT)
        self.RELAY3 = Pin(3, Pin.OUT)

        self.TRAIN1 = TrainTrack(6, 7, 8),
        self.TRAIN2 = TrainTrack(9, 10, 11),

    def run_once(self):
        """One iteration of our main loop.
        """
        for ir_sensor in self.ir_sensors:
            detected, has_changed = ir_sensor()
            if has_changed:
                if detected:
                    print('Train arriving', ir_sensor.name)
                else:
                    print('Train departing', ir_sensor.name)

        for button in self.buttons:
            pressed, has_changed = button()
            if has_changed:
                if pressed:
                    print('Button pressed', button.name)
                else:
                    print('Button released', button.name)

    def run_forever(self):
        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print('Exception:', e.__class__.__name__, e)
            utime.sleep(MAIN_LOOP_TIME)


if __name__ == '__main__':
    scene_control = SceneControl()

    print("@Whee! Pulsing LED!")
    scene_control.LED3(100)
    scene_control.LED3(0)

    print("Starting main loop...")
    scene_control.run_forever()
