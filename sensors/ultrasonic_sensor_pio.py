from machine import Pin
import rp2
import time
import micropython
import machine

"""
Pico runs at 125 MHz. The min. state machine (sm) frequency is 1908 Hz.
If the frequency is set to 1MHz, it should result in one cycle every 1 us, thats enough accuracy.

TRIGGER     -> Set pin
ECHO        -> Input pin

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


def calc_dist_m(time_sec_both_ways):
    return SOUND_VELOCITY_M_S * time_sec_both_ways / 2


def main(sm:rp2.StateMachine):
    """Read the output FIFO."""

    while True:
        
        diff_step = 2**32 - 1 - sm.get() # 2^32 -1 is the start value of the state machine's register
        # each cycle lasts 1/freq = 0.5 us
        # We have 2 cycles per diff_step
        echo_time = diff_step * 2 * (1 / FREQUENCY)  # diff_steps * num_cycles_per_step * cycle_time 
        dist_m = calc_dist_m(echo_time)

        print(dist_m)
        time.sleep(0.1)

if __name__ == "__main__":
    rp2.PIO(0).remove_program()
    sm = rp2.StateMachine(0, measure_distance, freq=FREQUENCY, set_base=Pin(TRIGGER_GPIO, Pin.OUT), in_base=Pin(ECHO_GPIO, Pin.IN), jmp_pin=Pin(ECHO_GPIO))
    sm.active(1)
    main(sm)