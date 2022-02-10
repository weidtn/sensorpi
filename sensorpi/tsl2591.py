#!/usr/bin/env python3
import board
import adafruit_tsl2591


def read_tsl2591():
    """
    Reads the sensor over I2C and returns the sensor class
    """
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_tsl2591.TSL2591(i2c)
    return sensor

def as_json(measurement, sensor_name="TSL2591", comment=None):
    """
    Reads the sensor and returns the data in the json format for influxdb
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
