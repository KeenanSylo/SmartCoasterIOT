# main.py -- put your code here!
import onewire, ds18x20, time
from machine import Pin
import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import random                 # Random number generator
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi 


led = Pin(2, Pin.OUT)
button = Pin(1, Pin.IN, Pin.PULL_DOWN)

ds_pin = machine.Pin(0)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()


def temp_sensor(r):
    ds_sensor.convert_temp()
    time.sleep_ms(50)
    for rom in r:
      tempC = ds_sensor.read_temp(rom)
      print('temperature (C):', "{:.2f}".format(tempC))
    time.sleep(1)


def send_temp():
    temp = temp_sensor(roms)
    print("Publishing: {0} to {1} ... ".format(temp, keys.AIO_TEMP_FEED), end='')
    try:
        client.publish(topic=keys.AIO_TEMP_FEED, msg=str(temp))
        print("DONE")
    except Exception as e:
        print("FAILED")


# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        if button.value()==0: 
          led.value(1)
          send_temp()

        elif button.value()==1:
          led.value(0)    # Send a random number to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.") 