#!/usr/bin/env python3
import board
import adafruit_dht

def read_dht11(pin):
    """returns (humidity,temperature) tuple from DHT sensor on given pin"""
    # board_pin = eval(f"board.D{pin}")
    board_pin = getattr(board, f"D{pin}")
    sensor = adafruit_dht.DHT11(board_pin, use_pulseio=False)
    return sensor

def as_json(measurement, pin, sensor_name="DHT11", comment=None):
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
