from machine import Pin


class Button:
    """Monitor a single pin for button presses.

    This class handles detecting and button presses and releases. When
    called it will report the current state of the button as well as
    whether that state has changed since the last time we were called.
    """
    def __init__(self, name, pin):
        self.name = name
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.last_value = self.new_value = self.pin.value()

    def __call__(self):
        """Returns (<bool>, <bool>) to indicate the button status.

        The first bool indicates whether the button is currently pressed
        (True) or released (False.)

        The second bool indicates whether the state of the button has
        changed since the last time we were queried.

        To handle debouncing the first state change is ignored. It is
        assumed that the caller will not call this function more than once
        in a given debounce period.
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
