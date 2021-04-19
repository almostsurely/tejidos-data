from __future__ import annotations

import concurrent
import os
import urllib.parse
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List

import requests

OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?{params}"

_CDMX_GRID = [(-99.3137552392332, 19.5586194307118),
             (-99.2394552392332, 19.5586194307118),
             (-99.1651552392332, 19.5586194307118),
             (-99.0908552392332, 19.5586194307118),
             (-99.0165552392332, 19.5586194307118),
             (-98.9422552392332, 19.5586194307118),
             (-99.3137552392332, 19.4881194307118),
             (-99.2394552392332, 19.4881194307118),
             (-99.1651552392332, 19.4881194307118),
             (-99.0908552392332, 19.4881194307118),
             (-99.0165552392332, 19.4881194307118),
             (-98.9422552392332, 19.4881194307118),
             (-99.3137552392332, 19.4176194307118),
             (-99.2394552392332, 19.4176194307118),
             (-99.1651552392332, 19.4176194307118),
             (-99.0908552392332, 19.4176194307118),
             (-99.0165552392332, 19.4176194307118),
             (-98.9422552392332, 19.4176194307118),
             (-99.3137552392332, 19.3471194307118),
             (-99.2394552392332, 19.3471194307118),
             (-99.1651552392332, 19.3471194307118),
             (-99.0908552392332, 19.3471194307118),
             (-99.0165552392332, 19.3471194307118),
             (-98.9422552392332, 19.3471194307118),
             (-99.3137552392332, 19.2766194307118),
             (-99.2394552392332, 19.2766194307118),
             (-99.1651552392332, 19.2766194307118),
             (-99.0908552392332, 19.2766194307118),
             (-99.0165552392332, 19.2766194307118),
             (-98.9422552392332, 19.2766194307118),
             (-99.3137552392332, 19.2061194307118),
             (-99.2394552392332, 19.2061194307118),
             (-99.1651552392332, 19.2061194307118),
             (-99.0908552392332, 19.2061194307118),
             (-99.0165552392332, 19.2061194307118),
             (-98.9422552392332, 19.2061194307118),
             (-99.3137552392332, 19.1356194307118),
             (-99.2394552392332, 19.1356194307118),
             (-99.1651552392332, 19.1356194307118),
             (-99.0908552392332, 19.1356194307118),
             (-99.0165552392332, 19.1356194307118),
             (-98.9422552392332, 19.1356194307118)]

@dataclass(frozen=True)
class Weather:
    temp: float
    wind_speed: float
    humidity: float
    latitude: float
    longitude: float

    def to_dict(self):
        return {key: str(value) for key, value in self.__dict__.items()}

class WeatherManager:

    _instance = None

    def __init__(self, api_key: str):
        self.api_key = api_key

    @classmethod
    def instance(cls) -> WeatherManager:
        if cls._instance is None:
            api_key = os.getenv("WHEATHER_API_KEY")
            if api_key is None:
                raise ValueError("Add WHEATHER_API_KEY as an environmental variable.")
            cls._instance = WeatherManager(api_key=api_key)
        return cls._instance

    def weather_from_lat_lon(self, latitude: str, longitude: str) -> Weather:
        url = OPEN_WEATHER_URL.format(params=urllib.parse.urlencode({"lat": latitude, "lon": longitude, "appid": self.api_key}))
        response = requests.get(url).json()
        return Weather(wind_speed=float(response.get("wind", {}).get("speed", 0.0)),
                       humidity=float(response.get("main", {}).get("humidity", 0.0)),
                       temp=float(response.get("main", {}).get("temp", 0.0)),
                       latitude=float(latitude),
                       longitude=float(longitude))

    def get_weather_cdmx(self) -> List[Weather]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return [future.result() for future in concurrent.futures.as_completed(
                [executor.submit(self.weather_from_lat_lon, latitude=point[1], longitude=point[0]) for point in
                 _CDMX_GRID])]


if __name__ == '__main__':
    lat = 19.4446544
    lon = -96.9543623
    import json
    import time
    seconds = time.time()
    weathers = WeatherManager.instance().get_weather_cdmx()
    seconds = time.time() - seconds
    print(f"{seconds} seconds")
    print(json.dumps([weather.to_dict() for weather in weathers], indent=4))
