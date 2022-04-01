#!/usr/bin/env python3
import board
import digitalio
import adafruit_bmp280

SENSORS = {}  # dictionary of initiated sensors


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
    return sensor


def bmp280_initspi(pin: int):
    """Initializes the sensor at given pin and adds to dict

    Otherwise the filesystem will have too many open files and the program will crash.
    Probably a bug in the adafruit library not properly closing the SPIDevice.
    """
    # get digital pin from board with integer
    board_pin = board.__getattribute__(f"D{pin}")
    spi = board.SPI()
    cs = digitalio.DigitalInOut(board_pin)
    sensor = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)
    SENSORS[pin] = sensor


def read_bmp280_spi(pin: int):
    """Reads the BMP280 over SPI on selected pin.

    Arguments:
        pin: The digital pin on the board as integer.

    Returns:
        bmp280: The sensor object containing the data as attributes.

    """
    if pin not in SENSORS:  # if not already initialized
        bmp280_initspi(pin)
    sensor = SENSORS[pin]
    return sensor


def i2c_as_json(measurement: str, address=0x76, sensor_name: str = "BMP280",
                comment: str = None, **kwargs):
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
                comment: str = None, **kwargs):
    try:
        sensor = read_bmp280_spi(pin)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure}
                 }]
        return json
    except Exception as e:
        print(e)
        print(f"Error reading sensor {sensor_name}. Is it connected?")

