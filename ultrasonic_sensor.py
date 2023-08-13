import micropython
import utime
from machine import Pin

micropython.alloc_emergency_exception_buf(100)

TOGGLE_GREEN_LT = 0.1
TOGGLE_RED_GT = 0.2
THRESHOLD = 0.02

# Pin 1,2,4
RED_GPIO = 0
YELLOW_GPIO = 1
GREEN_GPIO = 2

# Pin 9 / 10
TRIGGER_GPIO = 6
ECHO_GPIO = 7

SOUND_VELOCITY_M_S = 343


class UltrasonicDistanceMeasurement:
    def __init__(self, n_samples = 0):
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


def off():
    switch_to(None)

def switch_to(target_light):
    for light in lights:
        light.value(light == target_light)

def update_lights(distance_m):
    if distance_m < TOGGLE_GREEN_LT:
        switch_to(green)

    elif (
        TOGGLE_GREEN_LT + THRESHOLD
        < distance_m
        < TOGGLE_RED_GT - THRESHOLD
    ):
        switch_to(yellow)

    elif distance_m > TOGGLE_RED_GT:
        switch_to(red)


def main():
    sensor = UltrasonicDistanceMeasurement()

    try:
        while True:
            sensor.start_measurement()
            while sensor.distance_m is None:
                pass
            update_lights(sensor.distance_m)
            utime.sleep_ms(20)
    except KeyboardInterrupt:
        pass
    finally:
        off()


if __name__ == "__main__":
    red = Pin(RED_GPIO, Pin.OUT)
    yellow = Pin(YELLOW_GPIO, Pin.OUT)
    green = Pin(GREEN_GPIO, Pin.OUT)
    lights = [red, yellow, green]
    main()