import time
import functools
import json
import flask
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import requests

app = flask.Flask(__name__)

camera_ids = {"6713": "PIE (Outside CGH)",
              "7791": "TPE (Upper Changi North)",
              "6711": "PIE (Airport)",
              "3705": "ECP (NSRCC)"}


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ", ".join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, list):
        headers = ", ".join(x.upper() for x in headers)
    if not isinstance(origin, list):
        origin = ", ".join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers["allow"]

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == "OPTIONS":
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != "OPTIONS":
                return resp
            h = resp.headers
            h["Access-Control-Allow-Origin"] = origin
            h["Access-Control-Allow-Methods"] = get_methods()
            h["Access-Control-Max-Age"] = str(max_age)
            if headers is not None:
                h["Access-Control-Allow-Headers"] = headers
            return resp
        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@functools.lru_cache(maxsize=64, typed=False)
def retrieve_pollutants_external(h_timestamp):
    """
    Returns the maximum resolution readings for various pollutants.
    """
    try:
        API_URL = "https://api.data.gov.sg/v1/environment/psi"
        response = requests.get(API_URL).content
        readings = json.loads(response)["items"][0]["readings"]
        no2_1h = readings["no2_one_hour_max"]["east"]
        o3_8h = readings["o3_eight_hour_max"]["east"]
        co_8h = readings["co_eight_hour_max"]["east"]
        so2_24h = readings["so2_twenty_four_hourly"]["east"]
        psi_24h = readings["psi_twenty_four_hourly"]["east"]
    except Exception as e:
        print("Error!", e)
        no2_1h = "error"
        o3_8h = "error"
        co_8h = "error"
        so2_24h = "error"
        psi_24h = "error"
    output = {"no2_one_hour_max": no2_1h,
              "o3_eight_hour_max": o3_8h,
              "co_eight_hour_max": co_8h,
              "so2_twenty_four_hourly": so2_24h,
              "psi_twenty_four_hourly": psi_24h}
    return output

def get_realtime_weather_value(api_url, station_id="S107"):
    response = requests.get(api_url).content
    readings = json.loads(response)["items"][0]["readings"]
    output = "No Data"
    for reading in readings:
        if reading["station_id"] == station_id:
            output = reading["value"]
            break
    return output


def retrieve_weather_external():
    """
    Returns the maximum resolution readings for weather conditions.
    """
    try:
        air_temp = get_realtime_weather_value("https://api.data.gov.sg/v1/environment/air-temperature")
        rainfall = get_realtime_weather_value("https://api.data.gov.sg/v1/environment/rainfall")
        humidity = get_realtime_weather_value("https://api.data.gov.sg/v1/environment/relative-humidity")
        wind_direction = get_realtime_weather_value("https://api.data.gov.sg/v1/environment/wind-direction")
        wind_speed = get_realtime_weather_value("https://api.data.gov.sg/v1/environment/wind-speed")
        API_URL = "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
        response = requests.get(API_URL).content
        readings = json.loads(response)["items"][0]["forecasts"]
        for reading in readings:
            if reading["area"] == "Changi":
                forecast = reading["forecast"]
                break
    except Exception as e:
        print("Error!", e)
        air_temp = "error"
        rainfall = "error"
        humidity = "error"
        wind_direction = "error"
        wind_speed = "error"
        forecast = "error"
    output = {"air_temp": air_temp,
              "rainfall": rainfall,
              "humidity": humidity,
              "wind_direction": wind_direction,
              "wind_speed": wind_speed,
              "forecast": forecast}
    return output


@functools.lru_cache(maxsize=64, typed=False)
def retrieve_pm25_external(h_timestamp):
    try:
        API_URL = "https://api.data.gov.sg/v1/environment/pm25"
        response = json.loads(requests.get(API_URL).content)
        pm25_1h = response["items"][0]["readings"]["pm25_one_hourly"]["east"]
    except Exception as e:
        print("Error!", e)
        pm25_1h = "error"
    output = {"pm25_one_hourly": pm25_1h}
    return output


@functools.lru_cache(maxsize=64, typed=False)
def get_traffic_cam_images(calculate_m_timestamp):
    API_URL = "https://api.data.gov.sg/v1/transport/traffic-images"
    response = json.loads(requests.get(API_URL).content)
    cameras_list = response["items"][0]["cameras"]
    count, total_count = 0, len(list(camera_ids.keys()))
    output = {}
    for camera in cameras_list:
        if camera["camera_id"] in list(camera_ids.keys()):
            camera_img_url = camera["image"]
            output[camera["camera_id"]] = camera_img_url
            count += 1
            if count == total_count:
                break
    return output


def calculate_h_timestamp():
    return int(time.time()//3600)


def calculate_m_timestamp():
    return int(time.time()//60)


@app.route("/air_quality", methods=["GET"])
@crossdomain(origin="*")
def get_air_quality():
    """
    Returns the PSI and PM2.5 readings as a JSON.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        h_timestamp = calculate_h_timestamp()
        pollutants = retrieve_pollutants_external(h_timestamp)
        data["psi_24h"] = pollutants["psi_twenty_four_hourly"]
        data["pm25_1h"] = retrieve_pm25_external(h_timestamp)[
            "pm25_one_hourly"]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/pollutants", methods=["GET"])
@crossdomain(origin="*")
def get_pollutants():
    """
    Returns the pollutant readings as a JSON.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        h_timestamp = calculate_h_timestamp()
        pollutants = retrieve_pollutants_external(h_timestamp)
        data["no2_1h"] = pollutants["no2_one_hour_max"]
        data["o3_8h"] = pollutants["o3_eight_hour_max"]
        data["co_8h"] = pollutants["co_eight_hour_max"]
        data["so2_24h"] = pollutants["so2_twenty_four_hourly"]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/weather", methods=["GET"])
@crossdomain(origin="*")
def get_weather():
    data = {"success": False}
    if flask.request.method == "GET":
        weather_data = retrieve_weather_external()
        for key in list(weather_data.keys()):
            data[key] = weather_data[key]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/traffic_cam", methods=["GET"])
@crossdomain(origin="*")
def get_traffic_cam():
    data = {"success": False}
    if flask.request.method == "GET":
        m_timestamp = calculate_m_timestamp()
        cam_images = get_traffic_cam_images(m_timestamp)
        for key in list(cam_images.keys()):
            data[key] = cam_images[key]
        data["success"] = True
    return flask.jsonify(data)


# if file was executed by itself, start the server process
if __name__ == "__main__":
    print(" * [i] Starting Flask server")
    app.run(host="0.0.0.0", port=5000)
