from machine import Pin
import rp2
import time

"""Inverts 0 bitwise (32 bit integer) and outputs it. Result is (2^32)-1 = 4_294_967_295"""

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, autopush=True, autopull=True)
def test_output():
    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000
    
    mov(y, 31) #will set y to 32 bits = 2^32 -1 = 4_294_967_295
    # mov(y, ~null) # for 8, y has the value 2^32 - 2^(32-8-1) -1 = 2^32 - 2^23 - 1 = 4_286_578_687
    mov(isr, y)
    push()


rp2.PIO(0).remove_program()
sm = rp2.StateMachine(0, test_output, freq=1_000_000, set_base=Pin(25))
sm.active(1)

time.sleep(1)
print(sm.get())
sm.active(0)