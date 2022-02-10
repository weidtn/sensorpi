#!/usr/bin/env python3
import io
import time
import picamera
import cv2
import numpy as np

def capture(rotate=True):
    """
    Caputures image from the camera and returns in as opencv/numpy array
    """
    # Create the in-memory stream
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        camera.capture(stream, format='jpeg')
    # Construct a numpy array from the stream
    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    # "Decode" the image from the array, preserving colour
    image = cv2.imdecode(data, 1)
    if rotate:
        image = cv2.rotate(image, cv2.ROTATE_180)
    return image

def save_img(path, image):
    """
    Saves the image to the path on the filesystem
    """
    cv2.imwrite(path, image)

def calc_histogram(img):
    """
    Calculates histogram of grayscale image
    """
    hist = cv2.calcHist([img], channels=[0], mask=None, histSize=[256], ranges=[0,256])
    return hist.ravel()

def hist_as_json(measurement, sensor_name="Camera", rotate=True, comment=None):
    """
    Returns the integrated histogram value in json format for influxdb
    """
    hist = calc_histogram(capture(rotate))
    int_hist = integrate_histogram(hist)
    json= [{"measurement": measurement,
            "tags": {"sensor": sensor_name,
                     "comment": comment},
            "fields": {"Integrated Histogram": int_hist}}]
    return json

def integrate_histogram(hist):
    """
    Integrates the histogram
    TODO: Check method. Different results for numpy/by hand/scipy
    TODO: Maybe normalize?
    """
    return np.trapz(hist, dx=1)

def main():
    print(f"Integrated Histogram: {integrate_histogram(calc_histogram(capture()))}")

if __name__ == "__main__":
    main()
