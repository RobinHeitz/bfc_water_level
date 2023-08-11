from machine import Pin
from time import sleep

RED = 2
YELLOW = 3
GREEN = 4

def get_pins():
    p_red = Pin(RED, Pin.OUT)
    p_yellow = Pin(YELLOW, Pin.OUT)
    p_green = Pin(GREEN, Pin.OUT)
    return [p_red, p_yellow, p_green]

def main():
    ...
    pins = get_pins()
    for p in pins:
        p.on()

    while True:
        ...

def shutdown():
    for p in get_pins():
        p.off()



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
