# main.py -- put your code here!

import machine, onewire, ds18x20, time

ds_pin = machine.Pin(0)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)

while True:
  ds_sensor.convert_temp()
  time.sleep_ms(50)
  for rom in roms:
    tempC = ds_sensor.read_temp(rom)
    print('temperature (C):', "{:.2f}".format(tempC))
  time.sleep(1)
  