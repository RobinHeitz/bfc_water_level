import micropython
import utime
from machine import Pin

from helpers.read_config import read_config
from helpers.median import median
from helpers.wifi import connect_wifi

from sensors.ultrasonic_sensor_pio import UltraSonicMeasurementPIO
from sensors.ultrasonic_sensor import UltraSonicMeasurement

from traffic_lights.lights_distance_display import LightsDistanceDisplay

import urequests
import ujson

micropython.alloc_emergency_exception_buf(100)


class DistanceSensorController:

    def __init__(self, num_samples=10):
        self.num_samples = num_samples
        
        wifi_conf = read_config("wifi.json")
        connect_wifi(**wifi_conf)

        dist_conf = read_config("config.json")
        self.post_interval_ms = dist_conf["post_interval_ms"]
        self.backend_url = dist_conf["backend_url"]

        self.lights_controller = LightsDistanceDisplay(**dist_conf)
        self.sensor = UltraSonicMeasurement(self.dist_cb)


    def loop(self):
        self.start_tick = utime.ticks_ms()

        while True:
            print("Start measurement...")
            self.sensor.start_measurement(num_samples=self.num_samples)
            utime.sleep_ms(200)


    def post_sensor_data(self, water_height):
        print(f"post_sensor_data: {water_height=}")
        post_data = ujson.dumps({"water_level":water_height})
        res = urequests.post(self.backend_url, headers = {'content-type': 'application/json'}, data = post_data)
        res.close()


    def dist_cb(self, dist_list:list):
        med_water_height = median(dist_list)
        self.lights_controller.update_lights(med_water_height)

        if utime.ticks_diff(utime.ticks_ms(), self.start_tick) > self.post_interval_ms:
            self.start_tick = utime.ticks_ms()
            self.post_sensor_data(med_water_height)


def main():
    sensor_controller = DistanceSensorController(num_samples=10)
    sensor_controller.loop()


if __name__ == "__main__":
    main()