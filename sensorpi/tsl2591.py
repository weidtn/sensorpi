#!/usr/bin/env python3
import board
import adafruit_tsl2591


def read_tsl2591(sensor="tsl2591", comment=None):
    """
    Reads the sensor over I2C
    TODO Make return into JSON-like map for influxdb"""
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_tsl2591.TSL2591(i2c)
    return sensor


def main():
    data = read_tsl2591()
    print(f"Lux: {data.lux}\nIR: {data.infrared}\nVis: {data.visible}\nFull spectrum: {data.full_spectrum}")

if __name__ == "__main__":
    main()
