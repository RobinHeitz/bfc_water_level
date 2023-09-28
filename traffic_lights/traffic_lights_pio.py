import machine
import rp2
import micropython

import time
import rp2
from machine import Pin

"""This example uses 3 state machines to control 3 leds connected to gpios 0, 1 and 2."""

# Define the blink program.  It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blinking visible by eye.
# It's on/ off 160 ticks each. With 2kHz this means one tick lasts 1/2000 sec, 160 ticks therefore 0.08 sec.

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    set(pins, 0)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    wrap()


def main(state_machines):
    # Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the Pico board)

    for sm in state_machines:
        sm.active(1)
 
    time.sleep(5)
    raise Exception("Time is over.")


if __name__ == "__main__":
    
    rp2.PIO(0).remove_program()
    state_machines = []
    for i in range(3):
        state_machines.append(
            rp2.StateMachine(i, blink, freq=2000, set_base=Pin(i))
        )

    try:
        main(state_machines)

    except Exception:
        for sm in state_machines:
            sm.active(0)
    
    finally:
        for sm in state_machines:
            sm.exec('set(pins, 0)')
    
