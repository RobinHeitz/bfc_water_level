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

micropython.alloc_emergency_exception_buf(100)


    # let trigger_program = pio_proc::pio_asm!(
    #     ".wrap_target",
    #     "set pins, 1 [31]",
    #     "set pins, 0 [31]",
    #     "mov y !null",
    #     "wait 1 pin 0",
    #     "count:",
    #     "jmp y-- decrement",
    #     "decrement:",
    #     "jmp pin count",
    #     "mov isr y",
    #     "push block" ,
    #     ".wrap"
    # );
    # mov(y, ~null)
    # mov(isr, y)
    # push()


@rp2.asm_pio(autopush=True, set_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW)
def measure_distance():
    wrap_target()

    set(pins, 1) [9]     # lasts 10 us
    set(pins, 0)
    mov(y, ~null)           # y's value is: 4_294_967_295
    wait(1, pins, 0)        # wait until input pin at location 0 is HIGH
    
    
    label("count")
    jmp(y_dec, "decrement")
    label("decrement")
    jmp(pins, "count")
    mov(isr, y)
    push()

    wrap()


def main(sm:rp2.StateMachine):
    """Read the output FIFO."""

    while True:
        print(sm.get())


if __name__ == "__main__":
    rp2.PIO(0).remove_program()
    sm = rp2.StateMachine(0, measure_distance, freq=1_000_000, set_base=Pin(TRIGGER_GPIO, Pin.OUT), in_base=Pin(ECHO_GPIO, Pin.IN))
    sm.active(1)
    main(sm)