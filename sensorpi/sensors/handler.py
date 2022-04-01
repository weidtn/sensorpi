#!/usr/bin/env python3
from . import ds18b20, tsl2591, dht11, camera, bmp280, bme280


# This is a dictionary containing the function for each sensor
sensor_funcs = {
    "ds18b20": ds18b20.as_json,
    "tsl2591": tsl2591.as_json,
    "dht11": dht11.as_json,
    "camera": camera.hist_as_json,
    "camera_save": camera.save_img,
    "camera_capture": camera.capture,
    "bmp280spi": bmp280.spi_as_json,
    "bmp280i2c": bmp280.i2c_as_json,
    "bme280spi": bme280.spi_as_json,
    "bme280i2c": bme280.i2c_as_json,
}


def collect_measurements(sensors, measurement, timestamp, log):
    """
    takes a list of sensors with pins and runs measurements,
    then constructs a json wich is returned
    -----------------------------------------
    TODO: Check if connected
    """
    all_data = []
    for name in sensors:
        try:
            typ = sensors[name]["type"]
            sensor = sensors[name]
            if "save" in sensor:
                capture = sensor_funcs[typ+"_capture"](**sensor)
                sensor_funcs[typ+"_save"](capture, **sensor["save"], **sensor)
            if "protocol" not in sensor:
                sensor["protocol"] = ""  # calling the right function for sensors without protocols
            try:
                data = sensor_funcs[typ+sensor["protocol"]](measurement,
                                                            sensor_name=name,
                                                            **sensor)
                all_data.append(data[0])
            except Exception as e:
                log.warning(f"{e}")
                log.warning(f"Sensor {sensor} did not return a measurement!")
        except KeyError:
            log.warning(f"Sensor {sensor} is found in your config.edn "
                        f"but the type {typ} is not implemented (yet). "
                        "No measurement was taken for this sensor!")
    # the pipe symbol is the merge operator (python 3.9+):
    all_data_timestamp = [data | {"timestamp": timestamp} for data in all_data]
    return all_data_timestamp
