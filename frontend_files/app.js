document.addEventListener('DOMContentLoaded', function () {
    console.log("Started!");
    // PIE (Outside CGH)
    var cam_6713 = document.getElementById("cam_6713");
    // TPE (Upper Changi North)
    var cam_7791 = document.getElementById("cam_7791");
    // PIE (Airport)
    var cam_6711 = document.getElementById("cam_6711");
    // ECP (NSRCC)
    var cam_3705 = document.getElementById("cam_3705");

    var display_psi_24h = document.getElementById("psi_24h");
    var display_pm25_1h = document.getElementById("pm25_1h");
    var display_no2_1h = document.getElementById("no2_1h");
    var display_o3_8h = document.getElementById("o3_8h");
    var display_co_8h = document.getElementById("co_8h");
    var display_so2_24h = document.getElementById("so2_24h");

    console.log("Making requests...");
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

    console.log("Done!");
});