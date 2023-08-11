from machine import Pin
import utime
import micropython

micropython.alloc_emergency_exception_buf(100)

TOGGLE_GREEN_LT = 0.1
TOGGLE_RED_GT = 0.2
THRESHOLD = 0.02

# Pin 1,2,4
RED_GPIO = 0
YELLOW_GPIO = 1
GREEN_GPIO = 2


# Pin 9 / 10
TRIGGER_GPIO = 6
ECHO_GPIO = 7

SOUND_VELOCITY_M_S = 343

class Measurement:

    def __init__(self, freq_hz = 5):
        self.freq_hz = freq_hz

        self.trigger = Pin(TRIGGER_GPIO, Pin.OUT)
        self.echo = Pin(ECHO_GPIO, Pin.IN, Pin.PULL_DOWN)
        self.echo.irq(self.irq_callback, self.echo.IRQ_FALLING, hard=True)
        
        self.echo_start = utime.ticks_us()
        self.echo_end = utime.ticks_us()
        self.finished_measurement = False

        self.red = Pin(RED_GPIO, Pin.OUT)
        self.yellow = Pin(YELLOW_GPIO, Pin.OUT)
        self.green = Pin(GREEN_GPIO, Pin.OUT)
        self.current_light = None
        
        self.lights_off = {RED_GPIO: [self.yellow, self.green], YELLOW_GPIO: [self.green, self.red], GREEN_GPIO: [self.yellow, self.red]}
        self.lights = {RED_GPIO: self.red, YELLOW_GPIO: self.yellow, GREEN_GPIO: self.green}


    def off(self):
        for p in self.lights.values():
            p.low()


    def signal_length_to_distance_m(self, diff_us):
        diff_s = diff_us / 1e6
        distance_m = SOUND_VELOCITY_M_S * diff_s / 2
        print("Distance in m: ", distance_m)
        return distance_m


    def toggle(self, gpio):
        self.lights[gpio].high()
        for p in self.lights_off[gpio]:
            p.low()


    def control_lights(self, distance_m):
        TOGGLE_GREEN_COND = distance_m < TOGGLE_GREEN_LT
        TOGGLE_YELLOW_COND = TOGGLE_GREEN_LT + THRESHOLD < distance_m < TOGGLE_RED_GT - THRESHOLD
        TOGGLE_RED_COND = distance_m > TOGGLE_RED_GT
        
        if TOGGLE_GREEN_COND and self.current_light != GREEN_GPIO:
            self.toggle(GREEN_GPIO)
        
        elif TOGGLE_YELLOW_COND and self.current_light != YELLOW_GPIO:
            self.toggle(YELLOW_GPIO)
        
        elif TOGGLE_RED_COND and self.current_light != RED_GPIO:
            self.toggle(RED_GPIO)
            

    def loop(self):
        while True:
            self.measure()
            while self.finished_measurement == False:
                utime.sleep(1 / self.freq_hz)
            
            diff = utime.ticks_diff(self.echo_end, self.echo_start)
            self.finished_measurement = False
            distance_m = self.signal_length_to_distance_m(diff)
            self.control_lights(distance_m)


    def measure(self):
        self.trigger.high()
        utime.sleep_us(10)
        self.trigger.low()

        while self.echo.value() == 0:
            pass
        
        self.echo_start = utime.ticks_us()
       

    def irq_callback(self, _):
        self.echo_end = utime.ticks_us()
        self.finished_measurement = True


if __name__ == "__main__":
    m = Measurement()
    try:
        m.loop()
    except KeyboardInterrupt:
        m.off()
