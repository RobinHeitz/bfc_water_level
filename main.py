import micropython
import utime
from machine import Pin
from helpers.read_config import read_config
from sensors.ultrasonic_sensor_pio import UltraSonicMeasurementPIO
import urequests
import ujson

micropython.alloc_emergency_exception_buf(100)

SSID = "SlowMotion"
KEY = "23SpaziertHerein76"

TOGGLE_GREEN_LT_KEY = "TOGGLE_GREEN_LT"
TOGGLE_RED_GT_KEY = "TOGGLE_RED_GT"
THRESHOLD_KEY = "THRESHOLD"

RED_GPIO = 2
YELLOW_GPIO = 1
GREEN_GPIO = 0


def off():
    switch_to(None)

def switch_to(target_light):
    for light in lights:
        light.value(light == target_light)

def update_lights(distance_m, TOGGLE_GREEN_LT, TOGGLE_RED_GT, THRESHOLD):
    if distance_m < TOGGLE_GREEN_LT:
        switch_to(green)

    elif (
        TOGGLE_GREEN_LT + THRESHOLD
        < distance_m
        < TOGGLE_RED_GT - THRESHOLD
    ):
        switch_to(yellow)

    elif distance_m > TOGGLE_RED_GT:
        switch_to(red)


def sample_measurements(sensor:UltrasonicDistanceMeasurement, num_iters=10):
    """Takes 'num_iters' measurements and returns median measurement."""
    measurements = []
    for _ in range(num_iters):
            sensor.start_measurement()
            while sensor.distance_m is None:
                pass
            measurements.append(sensor.distance_m)
            utime.sleep_ms(20)
    measurements_sorted = sorted(measurements)

    indx = num_iters // 2
    if num_iters % 2 == 1:
        return measurements_sorted[indx]
    else:
        mean_val = 0.5 * (measurements_sorted[indx] + measurements_sorted[indx + 1])
        return mean_val


def post_sensor_data(water_height):
    print("post_sensor_data")
    data = {"water_level":water_height}
    post_data = ujson.dumps(data)

    request_url = "https://smarthome-frontend.onrender.com/bfc/water-lvl/"
    urequests.post(request_url, headers = {'content-type': 'application/json'}, data = post_data)


def main(config):
    sensor = UltrasonicDistanceMeasurement()

    TOGGLE_GREEN_LT = config.get(TOGGLE_GREEN_LT_KEY, 0.1)
    TOGGLE_RED_GT = config.get(TOGGLE_RED_GT_KEY, 0.2)
    THRESHOLD = config.get(THRESHOLD_KEY, 0.02)

    post_data_frequency = 100
    post_data_counter = 0


    try:
        while True:
            median_measurement = sample_measurements(sensor)
            update_lights(median_measurement, TOGGLE_GREEN_LT, TOGGLE_RED_GT, THRESHOLD)
            if post_data_counter == post_data_frequency:
                post_data_counter = 0
                post_sensor_data(median_measurement)
            
            post_data_counter += 1
            utime.sleep(0.1)
    
    
    except Exception:
        pass
    finally:
        off()


if __name__ == "__main__":
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, KEY)

    config_path = "config.json"
    config = read_config(config_path)

    red = Pin(RED_GPIO, Pin.OUT)
    yellow = Pin(YELLOW_GPIO, Pin.OUT)
    green = Pin(GREEN_GPIO, Pin.OUT)
    lights = [red, yellow, green]
    main(config)