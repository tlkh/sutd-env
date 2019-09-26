import os
import datetime
import json
import requests
import functools

camera_ids = {"6713": "PIE (Outside CGH)",
              "7791": "TPE (Upper Changi North)",
              "6711": "PIE (Airport)",
              "3705": "ECP (NSRCC)"}

LRU_CACHE_SIZE = 32
DATAMALL_KEY = os.environ["DATAMALL_KEY"]

@functools.lru_cache(maxsize=LRU_CACHE_SIZE, typed=False)
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
        air_temp = get_realtime_weather_value(
            "https://api.data.gov.sg/v1/environment/air-temperature")
        rainfall = get_realtime_weather_value(
            "https://api.data.gov.sg/v1/environment/rainfall")
        humidity = get_realtime_weather_value(
            "https://api.data.gov.sg/v1/environment/relative-humidity")
        wind_direction = get_realtime_weather_value(
            "https://api.data.gov.sg/v1/environment/wind-direction")
        wind_speed = get_realtime_weather_value(
            "https://api.data.gov.sg/v1/environment/wind-speed")
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


@functools.lru_cache(maxsize=LRU_CACHE_SIZE, typed=False)
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


@functools.lru_cache(maxsize=LRU_CACHE_SIZE, typed=False)
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


def get_simei_bus():
    """
    Returns ETA for next bus (5) to Simei
    """
    API_URL = "http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode=96049"
    current_time = datetime.datetime.now().minute
    response = requests.get(
        API_URL, headers={"AccountKey": DATAMALL_KEY})
    response = json.loads(response.content)
    services = response["Services"]
    for service in services:
        if service["ServiceNo"] == "5":
            # get something like `2019-09-26T17:43:15+08:00`
            next_bus = service["NextBus"]["EstimatedArrival"]
            break
    next_bus = int(next_bus.split(":")[1])
    eta = next_bus - current_time
    if eta < 0:
        eta += 60
    return eta

