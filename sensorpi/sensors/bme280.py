#!/usr/bin/env python3
import board
import digitalio # For use with SPI
import adafruit_bme280.basic as adafruit_bme280

SENSORS = {}  # dictionary of initiated sensors


def read_bme280_i2c(address=0x76):
    i2c = board.I2C()
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
    return bme280


def bmp280_initspi(pin: int):
    """Initializes the sensor at given pin and adds to dict

    Otherwise the filesystem will have too many open files and the program will crash.
    Probably a bug in the adafruit library not properly closing the SPIDevice.
    """
    # get digital pin from board with integer
    board_pin = board.__getattribute__(f"D{pin}")
    spi = board.SPI()
    cs = digitalio.DigitalInOut(board_pin)
    sensor = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)
    SENSORS[pin] = sensor


def read_bme280_spi(pin: int):
    """Reads the BME280 over SPI on selected pin.

    Arguments:
        pin: The digital pin on the board as integer.

    Returns:
        bme280: The sensor object containing the data as attributes.

    """
    # get digital pin from board with integer
    if pin not in SENSORS:  # if not already initialized
        bmp280_initspi(pin)
    sensor = SENSORS[pin]
    return sensor


def i2c_as_json(measurement: str, address=0x76, sensor_name: str = "BME280",
                comment: str = None, **kwargs):
    try:
        sensor = read_bme280_i2c(address)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure,
                            "relative humidity": sensor.relative_humidity}
                 }]
        return json
    except Exception:
        print(f"Error reading sensor {sensor_name}. Is it connected?")


def spi_as_json(measurement: str, pin, sensor_name: str = "BME280",
                comment: str = None, **kwargs):
    try:
        sensor = read_bme280_spi(pin)
        json = [{"measurement": measurement,
                 "tags": {"sensor": sensor_name,
                          "comment": comment},
                 "fields": {"temperature": sensor.temperature,
                            "pressure": sensor.pressure,
                            "relative humidity": sensor.relative_humidity}
                 }]
        return json
    except Exception:
        print(f"Error reading sensor {sensor_name}. Is it connected?")
