#!/usr/bin/env python3
import io
import time
import picamera
import cv2
import numpy as np
import time
from typing import Union


def capture(rotate: bool = True, **kwargs) -> np.ndarray:
    """Captures image from the camera and returns in as opencv/numpy array.

    Capures an image from the camera as opencv/numpy array.
    Needs the legacy camera functionality of the Rapsberry Pi activated.
    Whenever Picamera2 is released, this will be used.

    Args:
        rotate: Rotate the image by 180° when True. Defaults to True for now.

    Returns:
        image: The numpy array containing the image.

    """
    # Create the in-memory stream
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        time.sleep(2)
        camera.capture(stream, format='jpeg')
    # Construct a numpy array from the stream
    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    # "Decode" the image from the array, preserving colour
    image = cv2.imdecode(data, 1)
    if rotate:
        image = cv2.rotate(image, cv2.ROTATE_180)
    return image


def save_img(image: np.ndarray, path: str, timestamp=False, **kwargs):
    """Saves the image to the path on the filesystem.

    Args:
        path: Path where the image gets saved.
        image: The array containing the image.

    Examples:
        save_img("./image.png", image)

    """
    if timestamp:
        filename = path.split("/")[-1]  # only the filename
        pth = path.split(filename)[0]  # rest of the path, without filename
        ending = filename.split(".")[-1]  # fileformat (like .png or .jpg)
        f = filename.split(".")[0] # filename without format ending
        t = time.strftime("%d_%m_%Y_%H_%M_%S")
        cv2.imwrite(f"{pth}{f}_{t}.{ending}", image)
    else:
        cv2.imwrite(path, image)


def calc_histogram(img: np.ndarray) -> np.ndarray:
    """Calculates histogram of grayscale image

    Args:
        img: Array containing image to calculate the histogram of.

    Returns:
        hist: Array containing the histogram.

    """
    hist = cv2.calcHist([img], channels=[0], mask=None,
                        histSize=[256], ranges=[0, 256]).ravel()
    return hist


def hist_as_json(measurement: str, sensor_name: str = "Camera",
                 rotate: bool = True, comment: str = None,
                 **kwargs):
    """Returns the integrated histogram value in json format for influxdb

    Args:
        measurement: Name of the measurement.
        sensor_name: Name of the sensor mainly for influxdb.
            Useful if more than one sensor are used. Defaults to "Camera".
        rotate: Rotates the image by 180° if True.
        comment: Comment for the measurement.

    Returns:
        json: The json with the integrated histogram for influxdb.

    Examples:
        hist_as_json("measurement1", sensor_name="RPiCamNoIRv2" rotate=False,
                     comment="not rotated")

    """
    hist = calc_histogram(capture(rotate))
    int_hist = integrate_histogram(hist)
    json = [{"measurement": measurement,
             "tags": {"sensor": sensor_name,
                      "comment": comment},
             "fields": {"Integrated Histogram": int_hist}}]
    return json


def integrate_histogram(hist: np.ndarray) -> Union[np.ndarray, np.float32]:
    """Integrates a given histogram

    Args:
        hist: The histogram to integrate.

    Returns:
        int_hist: The integral of the histogram.

    TODO:
        - Check method. Different results for numpy/by hand/scipy
        - Maybe normalize?

    """
    int_hist = np.trapz(hist, dx=1)
    return int_hist


def main():
    print(f"""Integrated Histogram:
           {integrate_histogram(calc_histogram(capture()))}""")


if __name__ == "__main__":
    main()
