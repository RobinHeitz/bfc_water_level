import micropython
from machine import Pin
import utime

TRIGGER_GPIO = 28
ECHO_GPIO = 22
SOUND_VELOCITY_M_S = 343


class UltrasonicDistanceMeasurement:
    def __init__(self, trigger_gpio=TRIGGER_GPIO, echo_gpio=ECHO_GPIO, n_samples = 0):
        self.process_echo = self._process_echo
        self.trigger = Pin(TRIGGER_GPIO, Pin.OUT)
        self.echo = Pin(ECHO_GPIO, Pin.IN, Pin.PULL_DOWN)
        self.echo_start = None
        self.distance_m = None
        self.echo.irq(
            self.irq_callback, Pin.IRQ_RISING | Pin.IRQ_FALLING, hard=True
        )
        self.n_samples = n_samples
        self.distance_list = []


    def _process_echo(self, echo_end):
        diff = utime.ticks_diff(echo_end, self.echo_start)
        self.distance_m = SOUND_VELOCITY_M_S * (diff / 1e6) / 2
        if self.n_samples > 0:
            if len(self.distance_list) == self.n_samples:
                self.distance_list.pop(0)
            self.distance_list.append(self.distance_m)
    

    def irq_callback(self, pin):
        if pin.value():
            self.echo_start = utime.ticks_us()
        else:
            micropython.schedule(self.process_echo, utime.ticks_us())


    def start_measurement(self):
        self.distance_m = None
        self.trigger.on()
        utime.sleep_us(10)
        self.trigger.off()