#!/usr/bin/env python3
import glob
import edn_format
from influxdb_client import InfluxDBClient
from .sensors import ds18b20, tsl2591, dht11, camera, bmp280, bme280
import logging
import time
from datetime import datetime
import argparse
import os


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
log.addHandler(handler)


def edn_to_map(x) -> dict:
    """Helper function to turn edn to a python dict.

    Taken from:
    https://github.com/swaroopch/edn_format/issues/76#issuecomment-749618312

    Args:
        x: An edn map from edn_format.

    """
    if isinstance(x, edn_format.ImmutableDict):
        return {edn_to_map(k): edn_to_map(v) for k, v in x.items()}
    elif isinstance(x, edn_format.ImmutableList):
        return [edn_to_map(v) for v in x]
    elif isinstance(x, edn_format.Keyword):
        return x.name
    else:
        return x


def find_config() -> str:
    """Tries to find the config file.

    Returns:
        The path string of the found config file.

    TODO:
        - Write function to create empty config file

    """
    config_paths = glob.glob("../config.edn")
    if not config_paths:
        log.debug("Find config entered if branch!")
        config_paths = glob.glob("./config.edn")
    if len(config_paths) > 1:
        log.error("More than one config file found. This should not be possible?")
    try:
        config_path = config_paths[0]
        return config_path
    except Exception:
        log.error("No config file found. Please create a new config.edn file!")


def read_config(config_path: str) -> dict:
    """Reads the given config file and parses it.

    The config should contain data about the influxdb and the sensors.
    This data is read and put into a dictionary that is used for further usage.

    Args:
        edn: The path of the config.edn file.

    Returns:
        config: A dict containing the config data

    """
    with open(config_path, "r") as f:
        lines = f.read()
        config = edn_format.loads(lines)
    config_dict = edn_to_map(config)
    return config_dict


def send_to_db(data, db, user=None, password=None,
               influx_url="http://localhost:8086",
               org="-", retention_policy="autogen"):
    """Sends the data to the influxdb into the database called db.

    Returns the response of the server.
    Default keywords are defaults from influx
    Its for a v1.8 influxdb. Might also work for v>=2
    """
    with InfluxDBClient(url=influx_url, token=f"{user}:{password}", org=org) as client:
        with client.write_api() as write_api:
            write_api.write(bucket=f"{db}/{retention_policy}", record=data)


def create_db(db, influx_host="localhost", influx_port=8086):
    """Creates a new database if not already existing

    """
    try:
        client = InfluxDBClient(host=influx_host, port=influx_port)
        dbs = [db["name"] for db in client.get_list_database()]
        if db not in dbs:
            client.create_database(db)
            print(f"Database {db} created.")
        else:
            print(f"Database {db} already exists!")
    except Exception:
        print("Error while creating database!")


def collect_measurements(sensors, measurement):
    """
    takes a list of sensors with pins and runs measurements,
    then constructs a json wich is returned
    -----------------------------------------
    TODO: Check if connected
    """
    all_data = []
    for sensor in sensors:
        if sensors[sensor]["type"] == "ds18b20":
            try:
                data = ds18b20.as_json(measurement, sensor, comment=None)
                all_data.append(data[0])
            except Exception:
                log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
        elif sensors[sensor]["type"] == "camera":
            try:
                rotate = sensors[sensor]["rotate"]
                if "save" in sensors[sensor]:
                    save_dict = sensors[sensor]["save"]
                    path = save_dict["path"]
                    if "timestamp" in save_dict and save_dict["timestamp"] == True:
                        path = f"{path.split('.png')[0]}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.png"
                    camera.save_img(path, camera.capture(rotate))
                if sensors[sensor]["hist"] == True:
                    data = camera.hist_as_json(measurement, sensor,
                                               rotate=rotate, comment=None)
                    all_data.append(data[0])
            except Exception as e:
                log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
        elif sensors[sensor]["type"] == "tsl2591":
            try:
                data = tsl2591.as_json(measurement, sensor, comment=None)
                all_data.append(data[0])
            except Exception:
                log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
        elif sensors[sensor]["type"] == "dht11":
            try:
                data = dht11.as_json(measurement, sensors[sensor]["pin"],
                                     sensor, comment=None)
                all_data.append(data[0])
            except Exception:
                log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
        elif sensors[sensor]["type"] == "bmp280":
            if sensors[sensor]["protocol"] == "i2c":
                try:
                    data = bmp280.i2c_as_json(measurement, sensors[sensor]["address"],
                                              sensor, comment=None)
                    all_data.append(data[0])
                except Exception:
                    log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
            if sensors[sensor]["protocol"] == "spi":
                try:
                    data = bmp280.spi_as_json(measurement, sensors[sensor]["pin"],
                                              sensor, comment=None)
                    all_data.append(data[0])
                except Exception:
                    log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
            else:
                log.warning(f"Protocol for sensor {sensor} not implemented yet!")
        elif sensors[sensor]["type"] == "bme280":
            if sensors[sensor]["protocol"] == "i2c":
                try:
                    data = bme280.i2c_as_json(measurement, sensors[sensor]["address"],
                                              sensor, comment=None)
                    all_data.append(data[0])
                except Exception:
                    log.warning(f"Sensor {sensors[sensor]} did not return a measurement!")
            else:
                log.warning(f"Protocol for sensor {sensor} not implemented yet!")
        else:  # sensor not implemented
            log.warning(f"Sensor {sensor} is found in your config.edn "
                            f"but the type {sensors[sensor]['type']} "
                            "is not implemented (yet). "
                            "No measurement was taken for this sensor!")
    log.info(f"{datetime.now().strftime('%H:%M:%S')} Wrote to database.")
    return all_data


def loop(seconds, sensors, measurement, config):
    """The main loop which is taking a measurement at a given interval.

    Args:
        seconds: The time between measurements
        sensors: The list of sensors from config
        measurement: The name of the measurement
        config: the config file

    """
    try:
        log.info(f"Program running!"
                 f" Taking measurement every {seconds} seconds."
                 f" Writing to database {config['influxdb']['db']} as measurement {measurement}"
                 "\nPress Ctrl-C to exit.")
        while True:
            data = collect_measurements(sensors, measurement)
            send_to_db(data, config["influxdb"]["db"])
            time.sleep(seconds)
    except KeyboardInterrupt:
        print("Program is exiting...")
    # except KeyError:
        # print("Your config has some error, try to fix it!")


def main(seconds, measurement, config, verbose):
    """Main function which reads the config file and then starts a loop.
    TODO: Second loop around that one that saves a picture
    """
    try:
        sensors = config["sensors"]
        loop(seconds, sensors, measurement, config)
    except KeyError:
        log.warning("No sensors defined. Add them in the config.edn file!")


def main_with_prompt():
    parser = argparse.ArgumentParser(description="Run measurements from different sensors and send data to an influx db.")
    parser.add_argument("--config", "-c", type=argparse.FileType("r"), help="config.edn file to use.")
    parser.add_argument("--measurement", "-m", type=str, help="Measurement name.")
    parser.add_argument("--interval", "-i", type=int, help="Interval between measurements in seconds.")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    args = parser.parse_args()
    if args.measurement == None:
        args.measurement = input("Name of the measurement: ")
    if args.interval == None:
        args.interval = int(input("Wait seconds between measurements: "))
    if args.config == None:
        config = read_config(find_config())
    else:
        args.config.close()  # We actually dont need the stream, just the name.
        config = read_config(args.config.name)
    main(args.interval, args.measurement, config, args.verbose)


if __name__ == "__main__":
    main_with_prompt()
