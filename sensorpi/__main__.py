#!/usr/bin/env python3
import glob
import edn_format
from influxdb import InfluxDBClient


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
    config_paths = glob.glob("./config.edn")
    if len(config_paths) > 1:
        print("More than one config file found. This should not be possible?")
    try:
        config_path = config_paths[0]
    except:
        print("No config file found. Please create a new config.edn file!")
    return config_path


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


def send_to_db(json, db, influx_host="localhost", influx_port=8086):
    """
    Sends the json data to the influxdb into the database called db.
    Returns the response of the server.
    Default keywords are defaults from influx
    """
    try:
        client = InfluxDBClient(database=db, host=influx_host, port=influx_port)
        res = client.write_points(json)
    except:
        print(f"Error: Nothing was written to database!\n{res}")
        res = None
    return res


def create_db(db, influx_host="localhost", influx_port=8086):
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
    TODO
    takes a list of sensors with pins and runs measurements,
    then constructs a json wich is returned
    -----------------------------------------
    json()
    for sensor in sensors:
        if sensor.type == "DHT11":
            dht11.as_json(measurement)
    """
    pass


def main():
    """
    TODO: Ask for data
    TODO: Main loop takes measurement every x seconds
    TODO: Second loop around that one that saves a picture
    """
    print("Not much in here for now...")


print(read_config(find_config()))


if __name__ == "__main__":
    main()
