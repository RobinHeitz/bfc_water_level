from machine import Pin
import rp2
import time

@rp2.asm_pio()
def count_triggers():

    mov(y, 31)  # init
    
    wrap_target()
    
    label("loop")
    wait(1, pins, 0)

    
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]
    nop() [31]

    mov(isr, y)
    push()

    jmp(y_dec, "loop")

    wrap()


# Create and start a StateMachine with blink_1hz, outputting on Pin(25)
rp2.PIO(0).remove_program()
sm = rp2.StateMachine(0, count_triggers, freq=2000, in_base=Pin(15))
sm.active(1)

while True:
    print(sm.get())

time.sleep(2.2)
print("End")
sm.active(0)
sm.exec('set(pins, 0)')