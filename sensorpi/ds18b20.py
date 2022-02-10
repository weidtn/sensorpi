#!/usr/bin/env python3
import glob
import time

def find_temperature_file():
    """
    Finds the device in the file system (in linux its a device file)
    """
    return f"{glob.glob('/sys/bus/w1/devices/28*')[0]}/w1_slave"

def read_sensor():
    """
    Reads the sensor's raw data
    """
    with open(find_temperature_file(), "r") as f:
        lines = f.readlines()
    return lines

def convert_to_celsius(raw_data):
    """
    Takes the raw data and converts it to degree celsius
    """
    return float(raw_data[1].split("t=")[-1]) / 1000.0

def as_json(measurement, sensor_name="DS18B20", comment=None):
    """
    Reads the temperature and returns it in the correct format for influxdb
    """
    try:
        c = convert_to_celsius(read_sensor())
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": c},
                 }]
        return json
    except:
        print(f"Error: DS18B20 could not be read.")

if __name__ == "__main__":
    print(f"Current temperature:{convert_to_celsius(read_sensor())} °C")
