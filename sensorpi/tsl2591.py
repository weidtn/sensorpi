#!/usr/bin/env python3
import board
import adafruit_tsl2591

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_tsl2591.TSL2591(i2c)

lux = sensor.lux
infrared = sensor.infrared
visible = sensor.visible
full_spectrum = sensor.full_spectrum

print(lux, infrared, visible, full_spectrum)
