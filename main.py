import time
import machine
import onewire
import ds18x20
from machine import Pin
from lib import keys
import wifiConnection
from adafruit import AdafruitIO
from machine import PWM
from buzzer import playsong, bequiet

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
        return tempC
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
    temp_c = max(29, min(32, temp_c))
    
    t = (temp_c - 29) / (32 - 29)

    red = int(t * 65535)
    green = 0
    blue = int((1 - t) * 65535)

    red_pwm.duty_u16(red)
    green_pwm.duty_u16(green)
    blue_pwm.duty_u16(blue)


try:
    ip = wifiConnection.connect()
    print("Connected to WiFi, IP:", ip)
except Exception as e:
    print("WiFi connection failed:", e)
    raise

connected = adafruit_io.connect()

song = ["E5","G5","A5","P","E5","G5","B5","A5","P","E5","G5","A5","P","G5","E5"]
last_button_state = button.value()
oncoaster_value = 0
buzz = False
try:
    if connected:
        while True:
            current_state = button.value()
            if current_state != last_button_state:
                send_oncoaster(current_state)
                check_and_send_oncoaster(current_state)
            if current_state == 0:
                while button.value() == 0:
                    temp = temp_sensor()
                    if temp is not None:
                        set_rgbcolor(temp)
                        send_temp(temp)
                        if temp >= 32 and buzz == False:
                            playsong(song)
                            bequiet()
                            buzz = True
                        time.sleep(2)
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
