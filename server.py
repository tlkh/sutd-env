import json
import flask
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import requests

import utils
import ext_api

app = flask.Flask(__name__)

# ephemeral state just for lab demo purposes
state = {"temp_vote_higher": 0,
         "temp_vote_lower": 0,
         "psi_vote_lower": 0,
         "psi_vote_higher": 0}

# hard-coded users just for lab demo purposes
users = {"webapp": "3194142933356828989"}

print(" * [i] List of users:")
print(users)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """
    This creates a decorator `@crossdomain` which allows the API to
    process CORS requests (eg when running on localhost).
    """
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


@app.route("/air_quality", methods=["GET"])
@crossdomain(origin="*")
def get_air_quality():
    """
    Returns the PSI and PM2.5 readings as a JSON.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        h_timestamp = utils.calculate_h_timestamp()
        pollutants = ext_api.retrieve_pollutants_external(h_timestamp)
        data["psi_24h"] = pollutants["psi_twenty_four_hourly"]
        data["pm25_1h"] = ext_api.retrieve_pm25_external(h_timestamp)[
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
        h_timestamp = utils.calculate_h_timestamp()
        pollutants = ext_api. retrieve_pollutants_external(h_timestamp)
        data["no2_1h"] = pollutants["no2_one_hour_max"]
        data["o3_8h"] = pollutants["o3_eight_hour_max"]
        data["co_8h"] = pollutants["co_eight_hour_max"]
        data["so2_24h"] = pollutants["so2_twenty_four_hourly"]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/weather", methods=["GET"])
@crossdomain(origin="*")
def get_weather():
    """
    Returns the weather readings as a JSON.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        weather_data = ext_api.retrieve_weather_external()
        for key in list(weather_data.keys()):
            data[key] = weather_data[key]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/traffic_cam", methods=["GET"])
@crossdomain(origin="*")
def get_traffic_cam():
    """
    Returns the URL to traffic camera images as a JSON.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        m_timestamp = utils.calculate_m_timestamp()
        cam_images = ext_api.get_traffic_cam_images(m_timestamp)
        for key in list(cam_images.keys()):
            data[key] = cam_images[key]
        data["success"] = True
    return flask.jsonify(data)


@app.route("/vote_item", methods=["POST"])
@crossdomain(origin="*")
def vote_item():
    """
    Authenticates and add votes to an item.
    """
    data = {"success": False}
    if flask.request.method == "POST":
        username = request.args.get("username")
        api_key = request.args.get("api_key")
        if username is None or api_key is None:
            data["message"] = "Require authentication!"
            return flask.jsonify(data)
        else:
            try:
                if api_key == users[username]:
                    item = request.args.get("item")
                    mod_state = str(request.args.get("mod_state"))
                    if item == "temp":
                        if mod_state == "1":
                            state["temp_vote_higher"] += 1
                        elif mod_state == "-1":
                            state["temp_vote_lower"] += 1
                        else:
                            data["message"] = "Invalid mod_state"
                            return flask.jsonify(data)
                    elif item == "psi":
                        if mod_state == "1":
                            state["psi_vote_higher"] += 1
                        elif mod_state == "-1":
                            state["psi_vote_lower"] += 1
                        else:
                            data["message"] = "Invalid mod_state"
                            return flask.jsonify(data)
                else:
                    data["message"] = "Authentication failed!"
                    return flask.jsonify(data)
            except Exception as e:
                print("Error:", e)
                print("Probably user not in database!")
                data["message"] = e
                return flask.jsonify(data)
            data = {"success": True}
            return flask.jsonify(data)


@app.route("/get_votes", methods=["GET"])
@crossdomain(origin="*")
def get_votes():
    """
    Returns the net votes on an item.
    """
    data = {"success": False}
    if flask.request.method == "GET":
        # temperature response
        if state["temp_vote_higher"] > state["temp_vote_lower"]:
            diff = str(state["temp_vote_higher"] - state["temp_vote_lower"])
            temp_text = diff + "people feel the temperature is higher."
        elif state["temp_vote_higher"] < state["temp_vote_lower"]:
            diff = str(state["temp_vote_lower"] - state["temp_vote_higher"])
            temp_text = diff + " people feel the temperature is lower."
        else:
            temp_text = "People think the temperature is accurate."
        # psi response
        if state["psi_vote_higher"] > state["psi_vote_lower"]:
            diff = str(state["psi_vote_higher"] - state["psi_vote_lower"])
            psi_text = diff + " people feel the PSI is higher."
        elif state["psi_vote_higher"] < state["psi_vote_lower"]:
            diff = str(state["psi_vote_lower"] - state["psi_vote_higher"])
            psi_text = diff + " people feel the PSI is lower."
        else:
            psi_text = "People think the PSI is accurate."
        data["temp"] = temp_text
        data["psi"] = psi_text
        data["success"] = True
    return flask.jsonify(data)


# if file was executed by itself, start the server process
if __name__ == "__main__":
    print(" * [i] Starting Flask server")
    app.run(host="0.0.0.0", port=5000)
