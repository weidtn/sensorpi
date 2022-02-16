#!/usr/bin/env python3
import board
import digitalio # For use with SPI
import adafruit_bmp280

def read_bmp280_i2c(address=0x76):
    i2c = board.I2C()
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=address)
    return bmp280


def i2c_as_json(measurement: str, address=0x76, sensor_name: str = "BMP280", comment: str = None):
    try:
        sensor = read_bmp280_i2c(address)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure}
                 }]
        return json
    except:
        print(f"Error reading sensor {sensor_name}. Is it connected?")
