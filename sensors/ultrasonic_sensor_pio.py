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


@rp2.asm_pio(set_init=rp2.PIO.IN_HIGH, autopull=True, autopush=True)
def measure_distance():
    mov(y, 31)           # y's value is: 4_294_967_295
    set(pins, 1) [9]
    set(pins, 0)
    # wait(1, gpio, 22)        # wait until input pin at location 0 is HIGH
    
    
    label("count")
    jmp(y_dec, "decrement")
    label("decrement")
    jmp(pins, "count")
    mov(isr, y)
    push()



def main(sm:rp2.StateMachine):
    """Read the output FIFO."""

    while True:
        print(sm.get())

    time.sleep(1)
    value = sm.get()
    print("WE GOT: ", value)
    

if __name__ == "__main__":
    rp2.PIO(0).remove_program()
    sm = rp2.StateMachine(0, measure_distance, freq=1_000_000, set_base=Pin(TRIGGER_GPIO), in_base=Pin(ECHO_GPIO), out_base=Pin(ECHO_GPIO))
    sm.active(1)
    try:
        main(sm)
    except KeyboardInterrupt:
        print("Shutdown")
        sm.active(0)
        # machine.reset()