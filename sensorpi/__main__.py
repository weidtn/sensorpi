#!/usr/bin/env python3
import glob
import edn_format
from influxdb_client import InfluxDBClient
from .sensors import ds18b20, tsl2591, dht11, camera
import logging
import time
import sys
from datetime import datetime

log = logging.getLogger(name=__name__)


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
    except:
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
    except:
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
            data = ds18b20.as_json(measurement, sensor, comment=None)
            all_data.append(data[0])
        elif sensors[sensor]["type"] == "camera":
            rotate = sensors[sensor]["rotate"]
            data = camera.hist_as_json(measurement, sensor,
                                       rotate=rotate, comment=None)
            all_data.append(data[0])
        elif sensors[sensor]["type"] == "tsl2591":
            data = tsl2591.as_json(measurement, sensor, comment=None)
            all_data.append(data[0])
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
        while True:
            log.info(f"Program running! Taking measurement every {seconds} seconds."
                     "Press Ctrl-C to exit.")
            data = collect_measurements(sensors, measurement)
            send_to_db(data, config["influxdb"]["db"])
            time.sleep(seconds)
    except KeyboardInterrupt:
        print("Program is exiting...")
    except KeyError:
        print("Your config has some error, try to fix it!")


def main(seconds, measurement, verbose=False):
    """Main function which reads the config file and then starts a loop.
    TODO: Second loop around that one that saves a picture
    """
    if verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)
    config = read_config(find_config())
    try:
        sensors = config["sensors"]
        loop(seconds, sensors, measurement, config)
    except KeyError:
        log.warning("No sensors defined. Add them in the config.edn file!")


def main_with_prompt():
    log = logging.getLogger(name=__name__)
    measurement = input("Name of the measurement: ")
    seconds = int(input("Wait seconds between measurements: "))
    main(seconds, measurement, verbose=True)


if __name__ == "__main__":
    main_with_prompt()
