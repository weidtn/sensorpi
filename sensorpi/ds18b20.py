#!/usr/bin/env python3
import glob
import time

def find_temperature_file():
    return f"{glob.glob('/sys/bus/w1/devices/28*')[0]}/w1_slave"

def read_sensor():
    with open(find_temperature_file(), "r") as f:
        lines = f.readlines()
    return lines

def convert_to_celsius(raw_data):
    return float(raw_data[1].split("t=")[-1]) / 1000.0

if __name__ == "__main__":
    print(f"Current temperature:{convert_to_celsius(read_sensor())} °C")
