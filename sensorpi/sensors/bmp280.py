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
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=address)
    return bmp280


def read_bmp280_spi(pin: int):
    """Reads the BMP280 over SPI on selected pin.

    Arguments:
        pin: The digital pin on the board as integer.

    Returns:
        bmp280: The sensor object containing the data as attributes.

    """
    # get digital pin from board with integer
    board_pin = board.__getattribute__(f"D{pin}")
    cs = digitalio.DigitalInOut(board_pin)
    spi = board.SPI()
    bmp280 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)
    return bmp280


def i2c_as_json(measurement: str, address=0x76, sensor_name: str = "BMP280",
                comment: str = None):
    try:
        sensor = read_bmp280_i2c(address)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure}
                 }]
        return json
    except Exception:
        print(f"Error reading sensor {sensor_name}. Is it connected?")


def spi_as_json(measurement: str, pin, sensor_name: str = "BMP280",
                comment: str = None):
    try:
        sensor = read_bmp280_spi(pin)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure}
                 }]
        return json
    except Exception:
        print(f"Error reading sensor {sensor_name}. Is it connected?")
