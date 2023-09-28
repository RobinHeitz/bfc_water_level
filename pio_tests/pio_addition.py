import machine
import rp2
import micropython

"""
Pop two 32 bit integers from the TX FIFO, add them together, and push the
result to the TX FIFO. Autopush/pull should be disabled as we're using
explicit push and pull instructions.

This program uses the two's complement identity x + y == ~(~x - y)
"""

micropython.alloc_emergency_exception_buf(100)


@rp2.asm_pio()
def addition():
    pull()
    mov(x, invert(osr))
    pull()
    mov(y, osr)
    jmp("test")

    label("incr")
    jmp(x_dec, "test")

    label("test")
    jmp(y_dec, "incr")
    mov(isr, invert(x))
    push()


def main():
    print("main()")
    sm.put(100)
    sm.put(200)

    val = sm.get()
    print("We got:", val)


if __name__ == "__main__":
    rp2.PIO(0).remove_program()
    sm = rp2.StateMachine(0, addition, freq=1000000)
    sm.active(1)
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown")
        sm.active(0)
        machine.reset()