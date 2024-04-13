import requests
import datetime
from dateutil import tz
from suntime import Sun, SunTimeException
from picamera2 import Picamera2
from libcamera import controls
import os
import json
import collections
import time
import detect
import cv2
import board
import busio
import adafruit_vl53l0x

ip_server = "10.0.0.71"

DEMO = True # no internet, also need to manually set up sunrise and sunset times

path_local = "/home/raspberrypi/Desktop/DO_NOT_DELETE/"
path_server_images = "/home/ece492/Desktop/Autonomous-Meteor-Detector-and-Tracker/server/server_imgs"
path_server_short_expo = "/home/ece492/Desktop/Autonomous-Meteor-Detector-and-Tracker/server/short_exposure_images"
path_server_meta = "/home/ece492/Desktop/Autonomous-Meteor-Detector-and-Tracker/server/server_metadata"
path_server_status = "/home/ece492/Desktop/Autonomous-Meteor-Detector-and-Tracker/server/server_logs"



def get_times():
    sun = Sun(lat, lon)
    try:
        sunrise_time = sun.get_sunrise_time().time()
        sunset_time = sun.get_sunset_time().time()
    except SunTimeException as e:
        print("Error in getting sunrise/sunset time\n\
        sunrise is manually set to 12:00 in UTC\n\
        sundown is manually set to 02:00 in UTC\n")
        sunrise_time = datetime.time(hour=12)
        sunset_time = datetime.time(hour=2)
    if DEMO:
        # sunrise time has to be larger than sunset time, given how the library works
        sunrise_time = datetime.time(hour=23, minute=59)
        sunset_time = datetime.time(hour=0, minute=0)
    return sunrise_time, sunset_time


def setup_camera():
    global picam2
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(buffer_count=2))
    picam2.set_controls({"ExposureTime": 10000,
                        "AnalogueGain": 0,
                        "AfMode": controls.AfModeEnum.Manual,
                        "LensPosition": 0.0,
                        "ExposureValue": 0,
                        "AeExposureMode": controls.AeExposureModeEnum.Normal})
    picam2.start()
    
def camera_long_expo():
    global picam2
    picam2.stop()
    picam2.configure(picam2.create_still_configuration(buffer_count=2))
    if DEMO:
        picam2.set_controls({"ExposureTime": 10000,
                            "AnalogueGain": 0,
                            "AfMode": controls.AfModeEnum.Manual,
                            "LensPosition": 0.0,
                            "ExposureValue": 0,
                            "AeExposureMode": controls.AeExposureModeEnum.Normal})
    else:
        picam2.set_controls({"ExposureTime": 30000000,
                            "AnalogueGain": 0,
                            "AfMode": controls.AfModeEnum.Manual,
                            "LensPosition": 0.0,
                            "ExposureValue": -7,
                            "AeExposureMode": controls.AeExposureModeEnum.Long})
    picam2.start()
                    
def camera_short_expo():
    global picam2
    picam2.stop()
    picam2.configure(picam2.create_still_configuration(buffer_count=2))
    picam2.set_controls({"ExposureTime": 10000,
                        "AnalogueGain": 0,
                        "AfMode": controls.AfModeEnum.Manual,
                        "LensPosition": 0.0,
                        "ExposureValue": 0,
                        "AeExposureMode": controls.AeExposureModeEnum.Normal})
    picam2.start()
    
def get_info_from_ip():
    global city, lat, lon 
    if DEMO:
        city = "Edmonton"
        lat = 53.459
        lon = -113.5227
    else:
        ip_raspberrypi = requests.get('https://api64.ipify.org?format=json').json()["ip"]
        response = requests.get(f'https://ipapi.co/{ip_raspberrypi}/json/').json()
        city = response.get("city")
        lat = response.get("latitude")
        lon = response.get("longitude")

def refresh_time():
    now = datetime.datetime.now(datetime.timezone.utc)
    global now_datetime, now_time
    now_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_time = now.time()

def send_image():
    os.system(f"scp {path_local}{now_datetime}.jpg ece492@{ip_server}:{path_server_images}")
    dict_metadata = {"Camera": 2, "location": city, "date": now_datetime}
    with open(f"{path_local}{now_datetime}_meta.json", "w") as metadata:
        json.dump(dict_metadata, metadata)
    os.system(f"scp {path_local}{now_datetime}_meta.json ece492@{ip_server}:{path_server_meta}")
    os.system(f"rm {path_local}{now_datetime}_meta.json")

def run_detection(now_datetime):
    #image = cv2.imread(f"{path_local}{now_datetime}.jpg")
    #detection_result = detect.detect_obstruction(image, False)
    #if detection_result is True:
    #    status = "BAD"
    #else:
    #    status = "GOOD"
    dist = vl53.range
    status = "GOOD"
    if dist > 60:
        status = "OBSTRUCTION_DETECTED"
    temp = float(os.popen("vcgencmd measure_temp").read()[5:9])
    status_deque.append({now_datetime: {"status": status, "temp": temp}})
    status_dict = {}
    for dic in status_deque:
        for key,value in dic.items():
            status_dict[key] = value
    with open(f"{path_local}2.txt", "w") as status:
        json.dump(status_dict, status)
    os.system(f"scp {path_local}2.txt ece492@{ip_server}:{path_server_status}")

def fill_deque(length):
    status_deque = collections.deque(maxlen=length)
    for i in range(length):
        i_str = str(i).zfill(2)
        status_deque.append({f"2020-01-01T00:00:{i_str}Z": {"status": "GOOD", "temp": 0}}) # filler
        i+=1
    return status_deque


if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    setup_camera()
    get_info_from_ip()
    sunrise_time, sunset_time = get_times()
    now = datetime.datetime.now(datetime.timezone.utc)
    now_time = now.time()
    global now_datetime, status_deque 
    now_datetime = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    status_deque = fill_deque(30)
    long_expo = False
    print(f'City: {city}\nlat: {lat}\tlon: {lon}\nsunrise(UTC): {sunrise_time}\nsunset(UTC): {sunset_time}\nnow_datetime(UTC): {now_datetime}\n')
    detection_time = 0
    if DEMO:
        detection_time = 2
    else:
        detection_time = 10 # 5 min if exposure time is 30 sec
    detection_i = detection_time - 1 # the first image will be detected
    while(1):
        sunrise_time, sunset_time = get_times()
        refresh_time()
        if(now_time >= sunset_time and now_time <= sunrise_time):
        # if nighttime, take a long exposure image, and send it back to server along with its metadata
            if(long_expo == False):
                camera_long_expo()
                long_expo = True
                refresh_time()
            picam2.capture_file(f"{path_local}{now_datetime}.jpg")
            send_image()
        else:
        # if daytime, take a short exposure image, which will be only used for obstruction detection
            if(long_expo == True):
                camera_short_expo()
                long_expo = False
                refresh_time()
            picam2.capture_file(f"{path_local}{now_datetime}.jpg")
        # if night run detection every a few images
        if(now_time >= sunset_time and now_time <= sunrise_time):
            if DEMO:
                run_detection(now_datetime)
                time.sleep(20)
            else:
                detection_i = detection_i + 1
                if(detection_i == detection_time):
                    run_detection(now_datetime)
                    detection_i = 0
        else:
            # if daytime, run detection on every short-exposure image (5mins between images)
            run_detection(now_datetime)
            if DEMO:
                os.system(f"scp {path_local}{now_datetime}.jpg ece492@{ip_server}:{path_server_short_expo}")
                time.sleep(10)
            else:
                time.sleep(5*60) # 5 mins
        os.system(f"rm {path_local}{now_datetime}.jpg")
