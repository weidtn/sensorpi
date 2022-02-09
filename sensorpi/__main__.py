#!/usr/bin/env python3
import io
import time
import glob
import numpy as np
import cv2
from influxdb import InfluxDBClient
from picamera import PiCamera
import dht11

if __name__ == "__main__":
    print("Main function running")
