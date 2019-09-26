document.addEventListener('DOMContentLoaded', function () {
    var cam_6713 = document.getElementById("cam_6713"); // PIE (Outside CGH)
    var cam_7791 = document.getElementById("cam_7791"); // TPE (Upper Changi North)
    var cam_6711 = document.getElementById("cam_6711"); // PIE (Airport)
    var cam_3705 = document.getElementById("cam_3705"); // ECP (NSRCC)
    var large_air_temp = document.getElementById("large_air_temp");
    var large_psi = document.getElementById("large_psi");
    var large_forecast = document.getElementById("large_forecast");
    var simei_bus_eta = document.getElementById("simei_bus_eta");
    var temp_votes = document.getElementById("temp_votes");
    var psi_votes = document.getElementById("psi_votes");
    var display_psi_24h = document.getElementById("psi_24h");
    var display_pm25_1h = document.getElementById("pm25_1h");
    var display_no2_1h = document.getElementById("no2_1h");
    var display_o3_8h = document.getElementById("o3_8h");
    var display_co_8h = document.getElementById("co_8h");
    var display_so2_24h = document.getElementById("so2_24h");
    var display_air_temp = document.getElementById("air_temp");
    var display_rainfall = document.getElementById("rainfall");
    var display_humidity = document.getElementById("humidity");
    var display_wind_direction = document.getElementById("wind_direction");
    var display_wind_speed = document.getElementById("wind_speed");

    // simei bus time
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/next_bus_simei");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        simei_bus_eta.innerHTML = json["next_bus"];
    };
    // weather
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/weather");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        display_air_temp.innerHTML = json["air_temp"];
        large_air_temp.innerHTML = json["air_temp"];
        display_rainfall.innerHTML = json["rainfall"];
        display_humidity.innerHTML = json["humidity"];
        display_wind_direction.innerHTML = json["wind_direction"];
        display_wind_speed.innerHTML = json["wind_speed"];
        large_forecast.innerHTML = json["forecast"];
    };
    // traffic cam images
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/traffic_cam");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        cam_6713.src = json["6713"];
        cam_7791.src = json["7791"];
        cam_6711.src = json["6711"];
        cam_3705.src = json["3705"];
    };
    // PSI
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/air_quality");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        display_psi_24h.innerHTML = json["psi_24h"];
        large_psi.innerHTML = json["psi_24h"];
        display_pm25_1h.innerHTML = json["pm25_1h"];
    };
    // Pollutants
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/pollutants");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        display_no2_1h.innerHTML = json["no2_1h"];
        display_o3_8h.innerHTML = json["o3_8h"];
        display_co_8h.innerHTML = json["co_8h"];
        display_so2_24h.innerHTML = json["so2_24h"];
    };
    // votes
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:5000/get_votes");
    xhr.send();
    xhr.onload = function () {
        var json = JSON.parse(this.responseText);
        temp_votes.innerHTML = json["temp"];
        psi_votes.innerHTML = json["psi"];
    };
});