#!/usr/bin/python3

from time import sleep
import requests
from datetime import datetime

"""
This program is designed to take in data from Weatherflow API and add the data to a file that Direwolf (packet radio)
can use to sent data to APRS (Automatic Packet Reporting System).
Tempest weather station: https://weatherflow.com/tempest-home-weather-system/
Weatherflow API = https://apidocs.tempestwx.com/reference/quick-start
Direwolf = https://packet-radio.net/direwolf/
Output file format: https://www.cumuluswiki.org/a/Wxnow.txt
"""

# Tempest API key. Use link in comments above to create an account and get API key
my_api_key = ""
# Tempest Station ID. Use link in comments to purchase and get your station ID.
station_id = ""
# file name and location
filename = "/home/pi/wxnow.txt"

while True:
    # Call to Weatherflow API
    url = f"https://swd.weatherflow.com/swd/rest/observations/stn/{station_id}?bucket=1&units_temp=f&units_wind=mph&" \
      f"units_pressure=mb&units_precip=in&units_distance=mi&api_key={my_api_key}"

    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    json_data = response.json() if response and response.status_code == 200 else None

    # grabbing data from API json indexes.
    wind_dir_api = json_data["obs"][0][5]
    # grabbing data from API json indexes and rounding to whole number.
    wind_api = round(json_data["obs"][0][3])
    wind_gust_api = round(json_data["obs"][0][4])
    temp_api = round(json_data["obs"][0][8])
    rain_last_hour_api = round(json_data["obs"][0][19], 2)
    rain_last_24_api = round(json_data["obs"][0][19], 2)
    rain_since_midnight_api = round(json_data["obs"][0][14], 2)
    humidity_api = round(json_data["obs"][0][9])
    barometric_api = json_data["obs"][0][7]

    # formatting for APRS file output. ":03" is to make sure we always have leading 3 digit padding on file output.
    # "<05" makes sure we pad 5 digits with zero
    wind_dir_out = f"{wind_dir_api:03}"
    wind_out = f"{wind_api:03}"
    wind_gust_out = f"{wind_gust_api:03}"
    temp_out = f"{temp_api:03}"
    rain_last_hour_out = f"{rain_last_hour_api:03}".replace('.', '')
    rain_last_24_out = f"{rain_last_24_api:<03}".replace('.', '')
    rain_since_midnight_out = f"{rain_since_midnight_api:03}".replace('.', '')
    humidity_out = f"{humidity_api:02}"
    barometric_out = f"{barometric_api:<05}".replace('.', '')

    # Check to see if rain = 0.0 if it does format to read 000
    if rain_last_hour_out == "00":
        rain_last_hour_out = "000"
    if rain_last_24_out == "00":
        rain_last_24_out = "000"
    if rain_since_midnight_out == "00":
        rain_since_midnight_out = "000"

    # Get time and format for output file
    # Getting epoch time from API request
    epoch_time = json_data["obs"][0][0]
    # Converting epoch time to datetime
    datetime_object = datetime.fromtimestamp(epoch_time)
    # formatting the datetime as per APRS spec "Feb 01 2009 12:34"
    datetime_formatted = datetime_object.strftime("%b %d %Y %H:%M")

    # create/open file for writing
    with open(f"{filename}", "w") as file:
        file.writelines(f"{datetime_formatted}\n{wind_dir_out}/{wind_out}g{wind_gust_out}t{temp_out}r{rain_last_hour_out}"
                        f"p{rain_last_24_out}P{rain_since_midnight_out}h{humidity_out}b{barometric_out}")

    # print responses for debug
    # print(json_data)
    # print(f"wind direction: {wind_dir_out}")
    # print(f"wind: {wind_out}")
    # print(f"wind gust: {wind_gust_out}")
    # print(f"temp: {temp_out}")
    # print(f"rain last hour: {rain_last_hour_out}")
    # print(f"rain last 24 hours: {rain_last_24_out}")
    # print(f"rain since midnight: {rain_since_midnight_out}")
    # print(f"humidity: {humidity_out}")
    # print(f"barometric pressure: {barometric_out}")

    # print(f"Epoch time: {epoch_time}")
    # print(f"Datetime: {datetime_object}")
    # print(f"{datetime_formatted}")

    sleep(60)
