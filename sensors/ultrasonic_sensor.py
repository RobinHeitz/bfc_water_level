import micropython
from machine import Pin
import utime
from helpers.median import median

TRIGGER_GPIO = 28
ECHO_GPIO = 22
SOUND_VELOCITY_M_S = 343


class UltraSonicMeasurement:

    def __init__(self, dist_cb, trigger_gpio=TRIGGER_GPIO, echo_gpio=ECHO_GPIO):
        """Initializes UltraSonicMeasurement

        Args:
            dist_cb (callable): Callback function with argument which is a list of measurements.
            trigger_gpio (int, optional): gpio of the sensor's trigger. Defaults to TRIGGER_GPIO.
            echo_gpio (int, optional): gpio of the sensor's echo. Defaults to ECHO_GPIO.
        """
        
        self.dist_cb = dist_cb
        self.process_echo = self._process_echo
        
        self.trigger = Pin(trigger_gpio, Pin.OUT)
        self.echo = Pin(echo_gpio, Pin.IN, Pin.PULL_DOWN)
        self.echo_start = None
        self.echo.irq(
            self.irq_callback, Pin.IRQ_RISING | Pin.IRQ_FALLING, hard=True
        )
        self.dist_list = []


    def _calc_dist_m(self, time_sec_both_ways):
        return SOUND_VELOCITY_M_S * time_sec_both_ways / 2

    
    def _process_echo(self, echo_end):
        diff = utime.ticks_diff(echo_end, self.echo_start)
        diff_sec = diff / 1e6
        distance_m = self._calc_dist_m(diff_sec)
        self.dist_list.append(distance_m)


    def irq_callback(self, pin):
        if pin.value():
            self.echo_start = utime.ticks_us()
        else:
            micropython.schedule(self.process_echo, utime.ticks_us())


    def start_measurement(self, num_samples):
        self.dist_list = []
        for _ in range(num_samples):
            self.trigger.on()
            utime.sleep_us(10)
            self.trigger.off()
            utime.sleep_ms(50)
        micropython.schedule(self.dist_cb, self.dist_list)
        

def callback_measurement(dist_list):
    print("callback_measurement", dist_list)
    median_dist = median(dist_list)
    print("Median distance = ", median_dist)


def main():
    sensor = UltraSonicMeasurement(callback_measurement)
    sensor.start_measurement(10)


if __name__ == "__main__":
    main()