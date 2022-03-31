#!/usr/bin/env python3
import board
import adafruit_tsl2591


def read_tsl2591() -> adafruit_tsl2591.TSL2591:
    """Reads the sensor over I2C and returns the sensor class

    Reads the sensor over I2C and returns a sensor class from adafruit_tsl2591.
    It contains the data in attributes.

    Returns:
        sensor: The sensor class from adafruit_tsl2591.
            Contains the data in attributes.

    Example:
        data = read_dsl2591()
        print(f"Lux:{data.lux}\nIR:{data.infrared}\nVis:{data.visible}\nFull:{data.full_spectrum}")

    """
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_tsl2591.TSL2591(i2c)
    return sensor


def as_json(measurement: str, sensor_name: str = "TSL2591",
            comment: str = None, **kwargs):
    """Reads the sensor and returns the data in the json format for influxdb

    Args:
        measurement: The name of the measurement.
        sensor_name: Name of the sensor.
            Useful if more than one sensor of the same type is used.
            Defaults to TSL2591.
        comment: Comment about the measurement/sensor.

    Returns:
        json: The json for influxdb containing the light sensor data.

    """
    try:
        sensor = read_tsl2591()
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"Lux": sensor.lux,
                            "IR": sensor.infrared,
                            "Vis": sensor.visible,
                            "Full": sensor.full_spectrum}
                 }]
        return json
    except:
        print(f"Error reading sensor {sensor_name}. Is it connected?")


def main():
    data = read_tsl2591()
    print(f"Lux: {data.lux}\nIR: {data.infrared}\nVis: {data.visible}\nFull spectrum: {data.full_spectrum}")


if __name__ == "__main__":
    main()
