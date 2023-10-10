from machine import Pin
import rp2
import time
import micropython
import machine

"""
TRIGGER     -> Set pin
ECHO        -> Input pin / Jump pin

- Set trigger to HIGH for 10us
- Count duration of ECHO beeing HIGH
"""

TRIGGER_GPIO = 28
ECHO_GPIO = 22
SOUND_VELOCITY_M_S = 343
FREQUENCY = 10_000_000

micropython.alloc_emergency_exception_buf(100)


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW)
def measure_distance():
    wrap_target()

    set(pins, 1) [29]     # lasts 10 us
    nop() [29]
    nop() [29]
    nop() [9]
    set(pins, 0)
    mov(y, 31)           # y's value is: 4_294_967_295
    wait(1, pin, 0)        # wait until input pin at location 0 is HIGH
    label("count")
    jmp(y_dec, "decrement")
    label("decrement")
    jmp(pin, "count")
    mov(isr, y)
    push()
    wrap()


def median(values):
    num_vals = len(values)
    values_sorted = sorted(values)
    indx = num_vals // 2
    if num_vals % 2 == 1:
        return values_sorted[indx]
    else:
        mean_val = 0.5 * (values_sorted[indx] + values_sorted[indx + 1])
        return mean_val


class UltraSonicMeasurementPIO:

    def __init__(self, trigger_gpio=TRIGGER_GPIO, echo_gpio=ECHO_GPIO, freq=FREQUENCY):
        self.freq = freq
        self.trigger=Pin(trigger_gpio)
        self.echo=Pin(echo_gpio)

        attrs = dict(
            freq=self.freq, 
            set_base=self.trigger,
            in_base=self.echo,
            jmp_pin=self.echo
        )

        rp2.PIO(0).remove_program()
        self.sm = rp2.StateMachine(0, measure_distance, **attrs)
        self.sm.active(1)
        time.sleep_ms(100)


    def _calc_dist_m(self, time_sec_both_ways):
        return SOUND_VELOCITY_M_S * time_sec_both_ways / 2
    

    def _num_pio_asm_loops(self):
        """
        The state machines register starts at 2^32 - 1. In each loop of the PIO assembler instructions, 
        the register is decreased by 1 as long the echo pin is high.
        Afterwards the current register value is pushed to the ISR. The number of loop iterations is:
        2^32 - 1 - <register value>.
        """
        return 2**32 - 1 - self.sm.get()
    

    def _echo_time(self, num_loop_cycles):
        """Each loop cycle lasts 2 instructions, meaning that the actual time the echo is high is calculated by 
        <num-of-loop-iterations> * 2 * <cycle-time>"""
        return num_loop_cycles * 2 * (1 / self.freq)


    def get_distance(self):
        """
        Each cycle is 1 / freq long. We have 2 cycles per step difference, meaning that the actual time the echo is high
        is calculated by <number-of-steps> * 2 * <cycle-time>."""
        num_iters = self._num_pio_asm_loops()
        echo_time = self._echo_time(num_iters)
        dist_m = self._calc_dist_m(echo_time)
        return dist_m
    

    def get_distance_median(self, num_iters=5):

        values = [self._num_pio_asm_loops() for _ in range(num_iters)]
        num_loop_iters_median = median(values)
        echo_time = self._echo_time(num_loop_iters_median)
        return self._calc_dist_m(echo_time)


def main():
    sensor = UltraSonicMeasurementPIO()

    while True:
        print(sensor.get_distance_median())
        # time.sleep_ms(100)

if __name__ == "__main__":
    main()