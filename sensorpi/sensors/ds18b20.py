#!/usr/bin/env python3
import glob


def find_temperature_file() -> str:
    """Finds the sensor device in the file system.

    In Linux the sensor device is represented by a device file
    somewhere in /sys/bus/w1/devices. This file can be found by using glob.
    It should always be in a folder beginning with 28.
    The correct file is w1_slave in this folder.

    Returns:
        loc: The location of the sensor device file as string.

    """
    loc = f"{glob.glob('/sys/bus/w1/devices/28*')[0]}/w1_slave"
    return loc


def read_sensor() -> str:
    """Reads the sensor's raw data.

    Uses find_temperature_file() to find the sensor device file and reads it.

    Returns:
        lines: The raw data from the sensor as string.

    """
    with open(find_temperature_file(), "r") as f:
        lines = f.readlines()
    return lines


def convert_to_celsius(raw_data: str) -> float:
    """Takes the raw data and converts it to degree celsius.

    The Temperature in Celsius can easily be taken from the raw data string.
    Just divide the last value of the string by 1000.

    Args:
        raw_data: The sensor device file's data retrieved from read_sensor().

    Returns:
        c: Temperature in celsius

    """
    c = float(raw_data[1].split("t=")[-1]) / 1000.0
    return c


def as_json(measurement: str, sensor_name: str = "DS18B20",
            comment: str = None):
    """Reads the temperature and returns it in the correct format for influxdb.

    Args:
        measurement: Name of the measurement.
        sensor_name: Name of the sensor.
            Useful if more than on sensor of the same type are used.
            Defaults to "DS18B20".
        comment: Comment about the measurement.

    Returns:
        json: The json body for influxdb containing the temperature in celsius.

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
