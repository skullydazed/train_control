from machine import Pin


class Button:
    def __init__(self, name, pin):
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
