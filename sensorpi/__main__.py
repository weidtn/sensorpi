#!/usr/bin/env python3
import glob
import edn_format
from influxdb_client import InfluxDBClient
from .sensors import handler
import logging
import time
from datetime import datetime
import argparse


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
hdlr = logging.StreamHandler()
log.addHandler(hdlr)


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
    except Exception as e:
        log.error(e)
        log.error("No config file found. Please create a new config.edn file!")


def create_config(path):
    """Creates a new config file at the given path

    Args:
        path: string of a path
    """
    content = """{:influxdb {:url \"http://localhost:8086\"
                          :db \"test\"}
                :sensors{
                   :ds18b20_1 ;; name of the sensor
                   {:type \"ds18b20\"}
                   :dht11_inside
                   {:type \"dht11\"
                    :pin 26}}} ;; Pin of the sensor """
    try:
        with open(path, "w") as f:
            f.write(content)
    except Exception as e:
        print(e)
        log.error(f"Could not create config file at {path}!")


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
        log.error("Error while creating database!")


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
            timestamp = time.time()
            data = handler.collect_measurements(sensors, measurement, timestamp)
            try:
                send_to_db(data, config["influxdb"]["db"])
                log.info(f"{datetime.now().strftime('%H:%M:%S')} Wrote to database.")
            except Exception as e:
                log.warning(e)
                log.warning("Could not send data to database! Is it online?")
            time.sleep(seconds - (time.time() - timestamp))  # wait 'seconds' without time used to measure
    except KeyboardInterrupt:
        log.warning("Program is exiting...")
    except KeyError as e:
        log.error(e)
        log.error("Your config has some error, try to fix it!")


def main(seconds, measurement, config, verbose):
    """Main function which reads the config file and then starts a loop.

    """
    try:
        sensors = config["sensors"]
        loop(seconds, sensors, measurement, config)
    except KeyError:
        log.warning("No sensors defined. Add them in the config.edn file!")


def main_with_prompt():
    parser = argparse.ArgumentParser(
        description="Run measurements from different sensors and send data to an influx db.")
    parser.add_argument("--config", "-c", type=argparse.FileType("r"),
                        help="config.edn file to use.")
    parser.add_argument("--measurement", "-m", type=str,
                        help="Measurement name.")
    parser.add_argument("--newconfig", "-n", type=str,
                        help="Creates a new config at the given path.")
    parser.add_argument("--interval", "-i", type=int,
                        help="Interval between measurements in seconds.")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    args = parser.parse_args()
    if args.newconfig is not None:
        create_config(args.newconfig)
        log.info(f"Config created at {args.newconfig}."
                 f"Edit it and restart the program with it!")
        exit()
    if args.measurement is None:
        args.measurement = input("Name of the measurement: ")
    if args.interval is None:
        args.interval = int(input("Wait seconds between measurements: "))
    if args.config is None:
        config = read_config(find_config())
    else:
        args.config.close()  # We actually dont need the stream, just the name.
        config = read_config(args.config.name)
    main(args.interval, args.measurement, config, args.verbose)


if __name__ == "__main__":
    main_with_prompt()
