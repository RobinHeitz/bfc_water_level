from machine import Pin
import rp2
import time

"""
Pico runs at 125 MHz. The min. state machine (sm) frequency is 1908 Hz.
If the frequency is set to 1MHz, it should result in one cycle every 1 us, thats enough accuracy.

TRIGGER is set to gpio 6 (pin 9) -> Set pin
ECHO is set to gpio 7 (pin 10) -> Input pin

- Set trigger to HIGH for 10us
- Count duration of ECHO beeing HIGH
"""

@rp2.asm_pio()
def measure():
    # wrap_target()

    # pull (and stall if empty) from TX FIFO into OSR = Output shift registers
    pull(block)
    mov(x,osr) # 1_000_000 * 5 is the max. number of steps we wait for a a echo signal (works like a timeout i guess)
    

    # gpio 6 is HIGH for 10us
    set(pins, 1)       
    nop()                   [8] 
    set(pins, 0)

    wait(1, gpio, 7)          # wait high on pin ECHO, afterwards: Count how long the 

    label("loop")
    jmp(pin, "dec")       # True if pin (jmp_pin is set), meaning: Is this pin still HIGH
    jmp("output")           # Gets called when ECHO pin is low (again)
    
    
    label("dec")
    jmp(x_dec, "loop")

    label("output")
    mov(osr,x)
    push()       # pushes isr into RX FIFO; noblock means it overwrites existing values, thus making the FIFO beeing up-to-date


def main(sm):
    """Read the output FIFO."""

    while True:
        print("Testing...")
        time.sleep(1)
    

if __name__ == "__main__":
    sm = rp2.StateMachine(0, measure, freq=1000000, in_base=Pin(7), set_base=Pin(6), jmp_pin=Pin(7))
    print("Init")
    sm.active(1)
    print("Activate")

    # 32 bit integer has range of: [−2_147_483_648; 2_147_483_647] -> max timeout to search for ECHO is therefore 2147 [sec] at 1MHz cycle frequency

    num_steps = 1_000_000 * 5 # wait 5 seconds
    sm.put(num_steps)

    time.sleep(1)

    print("After sleep")
    output = sm.get()
    print("We got: ", output)

