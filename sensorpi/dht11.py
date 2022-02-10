#!/usr/bin/env python3
import board
import adafruit_dht

def read_dht11(pin: int):
    """Reads the DHT11 sensor connected on the given pin.

    Reads the DHT11 sensor by using the adafruit circuitpython library. It reads the given board pin.

    Args:
        pin: The pin of the board the sensor is connected to.

    Returns:
        sensor: the sensor class from adafruit_dht which contains the data as attributes.

    Example:
        sensor = read_dht11(26)
        t = sensor.temperature
        h = sensor.humidity
        print(t,h)

    """
    board_pin = getattr(board, f"D{pin}")
    sensor = adafruit_dht.DHT11(board_pin, use_pulseio=False)
    return sensor

def as_json(measurement: str, pin: int, sensor_name: str = "DHT11", comment: str = None):
    """Reads the DHT11 sensor and returns in the correct json format for influxdb.

    Args:
        measurement: name of the measurement.
        pin: The pin of the board the sensor is connected to:
        sensor_name: Name of the sensor, useful if there are more than one. Defaults to DHT11.
        comment: Optional comment for the sensor/measurement

    Returns:
        json: the json body for sending the data to the influx database

    """
    sensor = read_dht11(pin)
    json = [{"measurement": measurement,
             "tags": {"sensor": sensor_name,
                      "comment": comment},
             "fields": {"temperature": sensor.temperature,
                       "humidity": sensor.humidity}
             }]
    return json

def main(pin=None):
    if pin == None:
        pin = input("Read DHT11 on GPIO Pin#: ")
    try:
        sensor = read_dht11(pin)
        h, t = sensor.humidity, sensor.temperature
        print(f"Humidity: {h}% \nTemperature: {t}°C")
    except:
        print("Error. Is the pin correct?")

if __name__ == "__main__":
    main()
