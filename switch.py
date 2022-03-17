"""micropython-debounce-switch

A MicroPython Class for Debouncing Switches.

<https://github.com/selfhostedhome/micropython-debounce-switch>

The check_state() function was added by Zach White <https://github.com/skullydazed>.
"""

import machine


class Switch(): # pylint: disable=too-few-public-methods
    """Switch Class

    Class for defining a switch. Uses internal state to debounce switch in
    software. To use switch, check the "new_value_available" member and the
    "value" member from the application.
    """
    def __init__(self, pin, checks=3, check_period=100):
        self.pin = pin
        self.irq_on()

        self.debounce_timer = machine.Timer(-1)
        self.new_value_available = False
        self.value = None
        self.prev_value = None
        self.debounce_checks = 0
        self.checks = checks
        self.check_period = check_period

    def irq_on(self):
        self.pin.irq(handler=self._switch_change, trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING)

    def irq_off(self):
        self.pin.irq(trigger=0)

    def check_state(self):
        """Returns the changed state of the switch, or None if no change.

        Returns:
            True    The button is currently pressed down
            False   The button is currently released
            None    The button state is the same as the last time you checked
        """
        to_return = None
        self.irq_off()

        if self.new_value_available:
            self.new_value_available = False
            to_return = self.value

        self.irq_on()
        return to_return

    def _switch_change(self, pin):
        self.value = pin.value()

        # Start timer to check for debounce
        self.debounce_checks = 0
        self._start_debounce_timer()

        # Disable IRQs for GPIO pin while debouncing
        self.pin.irq(trigger=0)

    def _start_debounce_timer(self):
        self.debounce_timer.init(period=self.check_period, mode=machine.Timer.ONE_SHOT,
                                 callback=self._check_debounce)

    def _check_debounce(self, _):
        new_value = self.pin.value()

        if new_value == self.value:
            self.debounce_checks = self.debounce_checks + 1

            if self.debounce_checks == self.checks:
                # Values are the same, debouncing done

                # Check if this is actually a new value for the application
                if self.prev_value != self.value:
                    self.new_value_available = True
                    self.prev_value = self.value

                # Re-enable the Switch IRQ to get the next change
                self.irq_on()
            else:
                # Start the timer over to make sure debounce value stays the same
                self._start_debounce_timer()
        else:
            # Values are not the same, update value we're checking for and delay again
            self.debounce_checks = 0
            self.value = new_value
            self._start_debounce_timer()
