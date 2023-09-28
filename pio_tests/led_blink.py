from machine import Pin
import rp2
import time

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_1hz():
    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000
    set(pins, 1)
    set(x, 31)                  [6]
    label("delay_high")
    nop()                       [29]
    jmp(x_dec, "delay_high")

    # Cycles: 1 + 7 + 32 * (30 + 1) = 1000
    set(pins, 0)
    set(x, 31)                  [6]
    label("delay_low")
    nop()                       [29]
    jmp(x_dec, "delay_low")



# Create and start a StateMachine with blink_1hz, outputting on Pin(25)
rp2.PIO(0).remove_program()
sm = rp2.StateMachine(0, blink_1hz, freq=2000, set_base=Pin(2))
sm.active(1)

time.sleep(2.2)
print("End")
sm.active(0)
sm.exec('set(pins, 0)')