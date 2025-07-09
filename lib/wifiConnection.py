import lib.keys as keys
import network
from time import sleep


def connect():
    wlan = network.WLAN(network.STA_IF)      
    if not wlan.isconnected():                  
        print('connecting to network...')
        wlan.active(True)                       
        wlan.config(pm = 0xa11140)
        wlan.connect(keys.WIFI_SSID, keys.WIFI_PASS)
        while not wlan.isconnected() and wlan.status() >= 0:
            print('.', end='')
            sleep(1)
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))
    return ip

def disconnect():
    wlan = network.WLAN(network.STA_IF)      
    wlan.disconnect()
    wlan = None 