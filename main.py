import time
import machine
import onewire
import ds18x20
from machine import Pin
from lib import keys  # Assuming keys.py contains your configuration keys
import wifiConnection
from adafruit import AdafruitIO  # Import your AdafruitIO class

led = Pin(2, Pin.OUT)
button = Pin(1, Pin.IN, Pin.PULL_DOWN)

ds_pin = machine.Pin(0)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()


def temp_sensor():
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
        print("Temperature (C): {:.2f}".format(tempC))
        return tempC  # Return the first temperature found
    return None

# Create an instance of AdafruitIO
adafruit_io = AdafruitIO()


def send_temp(temp):
    try:
        print("Publishing:", temp)
        adafruit_io.publish(feed_key=keys.AIO_FEEDS["temp"], value=temp)
        print(" ")
    except Exception as e:
        print("FAILED:", e)

def send_oncoaster(on):
    try:
        adafruit_io.publish(feed_key=keys.AIO_FEEDS["oncoaster"], value=on)
    except Exception as e:
        print("FAILED:", e)

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
    print("Connected to WiFi, IP:", ip)
except Exception as e:
    print("WiFi connection failed:", e)
    raise

# Use AdafruitIO class to connect to Adafruit IO
connected = adafruit_io.connect()

last_button_state = 0
try:
    if connected:
        while True:
            current_state = button.value()
            send_oncoaster(current_state)
            if current_state == 0:
                led.on()
                while button.value() == 0:  # Stay in loop while button is pressed
                    temp = temp_sensor()
                    send_temp(temp)
                    time.sleep(1)  # Limit update rate
                led.off()

            last_button_state = current_state
            time.sleep(0.1)

finally:
    if connected:
        adafruit_io.disconnect()
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")
