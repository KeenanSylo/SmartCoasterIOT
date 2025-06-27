import time
import machine
import onewire
import ds18x20
from machine import Pin
from lib import keys  # Assuming keys.py contains your configuration keys
import wifiConnection
from adafruit import AdafruitIO  # Import your AdafruitIO class
from machine import PWM

led = Pin(2, Pin.OUT)
button = Pin(1, Pin.IN, Pin.PULL_DOWN)
red_pwm = PWM(Pin(8))
green_pwm = PWM(Pin(7))
blue_pwm = PWM(Pin(6))

ds_pin = machine.Pin(0)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
adafruit_io = AdafruitIO()

for pwm in (red_pwm, green_pwm, blue_pwm):
    pwm.freq(1000)

def temp_sensor():
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
        print("Temperature (C): {:.2f}".format(tempC))
        return tempC  # Return the first temperature found
    return None


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


def check_and_send_oncoaster(current_state):
    global oncoaster_value, last_oncoaster_state
    if current_state == 1 and last_oncoaster_state == 0:
        oncoaster_value += 1
        try:
            adafruit_io.publish(feed_key=keys.AIO_FEEDS["totalcoaster"], value=oncoaster_value)
        except Exception as e:
            print("FAILED:", e)
    last_oncoaster_state = current_state


def set_rgbcolor(temp_c):
    # Clamp temp between 20 and 35
    temp_c = max(29, min(32, temp_c))
    
    # Normalize temp_c in range [29, 32] to [0.0, 1.0]
    t = (temp_c - 29) / (32 - 29)  # (temp - min) / (max - min)

    # Calculate RGB (linear fade: blue to red)
    red = int(t * 65535)
    green = 0
    blue = int((1 - t) * 65535)

    red_pwm.duty_u16(red)
    green_pwm.duty_u16(green)
    blue_pwm.duty_u16(blue)


# Try WiFi Connection
try:
    ip = wifiConnection.connect()
    print("Connected to WiFi, IP:", ip)
except Exception as e:
    print("WiFi connection failed:", e)
    raise

# Use AdafruitIO class to connect to Adafruit IO
connected = adafruit_io.connect()

last_button_state = button.value()
oncoaster_value = 0
try:
    if connected:
        while True:
            current_state = button.value()
            if current_state != last_button_state:
                send_oncoaster(current_state)
                check_and_send_oncoaster(current_state)
            if current_state == 0:
                led.on()
                while button.value() == 0:  # Stay in loop while button is pressed
                    temp = temp_sensor()
                    if temp is not None:
                        set_rgbcolor(temp)
                        send_temp(temp)
                        time.sleep(0.5)  # Limit update rate
                led.off()
                red_pwm.duty_u16(0)
                green_pwm.duty_u16(0)
                blue_pwm.duty_u16(0)

            last_button_state = current_state
            time.sleep(0.1)

finally:
    if connected:
        adafruit_io.disconnect()
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")
