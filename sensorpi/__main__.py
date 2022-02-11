#!/usr/bin/env python3
import io
import time
import glob
import numpy as np
import cv2
from influxdb import InfluxDBClient
from picamera import PiCamera
import dht11
import tsl2591
import ds18b20


def send_to_db(json, db, influx_host="localhost", influx_port=8086):
    """
    Sends the json data to the influxdb into the database called db. Returns the response of the server.
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


if __name__ == "__main__":
    main()
