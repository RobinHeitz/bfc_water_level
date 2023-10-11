import network
import utime

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print(f'Waiting for connection to {ssid}...')
        utime.sleep(1)
    print(wlan.ifconfig())

if __name__ == "__main__":
    from helpers.read_config import read_config
    conf = read_config("../wifi.json")
    connect_wifi(**conf)