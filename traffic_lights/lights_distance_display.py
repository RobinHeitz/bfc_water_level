from helpers.read_config import read_config
from machine import Pin


class LightsDistanceDisplay:

    def __init__(self, red_gpio, yellow_gpio, green_gpio, dist_green_lt, dist_red_gt, threshold, *args, **kwargs):
        
        self.red = Pin(red_gpio, Pin.OUT)
        self.yellow = Pin(yellow_gpio, Pin.OUT)
        self.green = Pin(green_gpio, Pin.OUT)
        self.lights = [self.red, self.yellow, self.green]

        self.dist_green_lt = dist_green_lt
        self.dist_red_gt = dist_red_gt
        self.threshold = threshold

    
    def off(self):
        self.switch_to(None)


    def switch_to(self, target_light):
        for light in self.lights:
            light.value(light == target_light)


    def update_lights(self, dist_m):
        if dist_m < self.dist_green_lt:
            self.switch_to(self.green)

        elif (
            self.dist_green_lt + self.threshold
            < dist_m
            < self.dist_red_gt - self.threshold
        ):
            self.switch_to(self.yellow)

        elif dist_m > self.dist_red_gt:
            self.switch_to(self.red)



if __name__ == "__main__":
    import utime
    
    conf = read_config("config.json")
    
    lights_display = LightsDistanceDisplay(**conf)
    for l in lights_display.lights:
        lights_display.switch_to(l)
        utime.sleep(1)
    
    lights_display.off()

