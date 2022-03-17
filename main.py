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

from button import Button
from led import LED
from train import Train

MAIN_LOOP_TIME = 0.005


class SceneControl:
    """Integrate all the hardware and provide controls for the scene.
    """
    def __init__(self):
        self.smoke = Pin(28, Pin.OUT)
        self.pi_led = LED('Pi Pico', 25)
        self.tram = Train('Tram', 6, 7, 8)
        self.carousel = Train('Carousel', 9, 10, 11)

        # Push buttons
        self.buttons = [
            Button('Stop', 4), 
            Button('Start', 14), 
            Button('Start', 15),
        ]

        # IR Sensors to detect train position
        self.ir_sensors = [
            Button('IR1', 16),
            Button('IR2', 17),
            Button('IR3', 18),
            Button('IR4', 19),
        ]

        # Devices I don't have assigned yet
        self.LED1 = LED('LED1', 7)
        self.LED2 = LED('LED2', 12)
        self.LED3 = LED('LED3', 13)

        self.RELAY2 = Pin(27, Pin.OUT)
        self.RELAY3 = Pin(3, Pin.OUT)

        # Initialize
        self.off()


    def off(self):
        """Turn the scene off.
        """
        self.smoke.off()
        self.pi_led(0)
        self.tram.stop()
        self.carousel.stop()
        self.LED1(0)
        self.LED2(0)
        self.LED3(0)
        self.RELAY2.off()
        self.RELAY3.off()

    def on(self, button):
        """Turn the scene on.
        """
        self.smoke.off()
        self.pi_led(25)
        self.tram.speed = 16384
        self.tram.forward()
        self.carousel.speed = 16384
        self.carousel.forward()
        self.LED1(75)
        self.LED2(75)
        self.LED3(75)
        self.RELAY2.off()
        self.RELAY3.off()

    def button_handler(self, button_name):
        """Dispatch button presses.
        """
        if button_name == 'Stop':
            print('Turning off scene')
            self.off()

        elif button_name == 'Start':
            print('Turning on scene', button_name)
            self.on()

        else:
            print('Unknown button', button_name)

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
            if pressed and has_changed:
                self.scene(button.name)

    def run_forever(self):
        """Run the main loop until forcibly stopped.
        """
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

    print("Pulsing LED:")
    scene_control.LED3(75)
    scene_control.LED3(0)

    print("\nStarting main loop...")
    scene_control.run_forever()
