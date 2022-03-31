#!/usr/bin/env python3
import board
import digitalio
import adafruit_bmp280


def read_bmp280_i2c(address=0x76):
    """Reads the BMP280 over I2C at selected address.

    Arguments:
        address: The i2c memory address. Defaults to 0x76,
            which should be default. Try 0x77 if it is not.

    Returns:
        bmp280: The sensor object containgin the data as attributes.

    """
    i2c = board.I2C()
    sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=address)
    return bmp280


def read_bmp280_spi(pin: int):
    """Reads the BMP280 over SPI on selected pin.

    Arguments:
        pin: The digital pin on the board as integer.

    Returns:
        bmp280: The sensor object containing the data as attributes.

    """
    # get digital pin from board with integer
    bmp280 = {}
    board_pin = board.__getattribute__(f"D{pin}")
    with board.SPI() as spi, digitalio.DigitalInOut(board_pin) as cs:
        sensor = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)
        bmp280["temperature"] = float(sensor.temperature)
        bmp280["pressure"] = float(sensor.pressure)
    board_pin = None
    return bmp280


def i2c_as_json(measurement: str, address=0x76, sensor_name: str = "BMP280",
                comment: str = None, **kwargs):
    try:
        sensor = read_bmp280_i2c(address)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor["temperature"],
                            "pressure": sensor["pressure"]}
                 }]
        return json
    except Exception:
        print(f"Error reading sensor {sensor_name}. Is it connected?")


def spi_as_json(measurement: str, pin, sensor_name: str = "BMP280",
                comment: str = None, **kwargs):
    try:
        sensor = read_bmp280_spi(pin)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor["temperature"],
                            "pressure": sensor["pressure"]}
                 }]
        return json
    except Exception as e:
        print(e)
        print(f"Error reading sensor {sensor_name}. Is it connected?")

