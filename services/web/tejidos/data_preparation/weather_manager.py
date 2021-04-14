from __future__ import annotations

import os
import urllib.parse
from dataclasses import dataclass

import requests

OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?{params}"

@dataclass(frozen=True)
class Weather:
    temp: float
    wind_speed: float
    humidity: float
    latitude: float
    longitude: float

    def to_dict(self):
        return self.__dict__

class WeatherManager:

    _instance = None

    def __init__(self, api_key: str):
        self.api_key = api_key

    @classmethod
    def instance(cls) -> WeatherManager:
        if cls._instance is None:
            api_key = os.getenv("WHEATHER_API_KEY")
            cls._instance = WeatherManager(api_key=api_key)
        return cls._instance

    def weather_from_lat_lon(self, latitude, longitude) -> Weather:
        url = OPEN_WEATHER_URL.format(params=urllib.parse.urlencode({"lat": lat, "lon": lon, "appid": self.api_key}))
        response = requests.get(url).json()
        return Weather(wind_speed=response.get("wind", {}).get("speed", 0.0),
                       humidity=response.get("main", {}).get("humidity", 0.0),
                       temp=response.get("temp", {}).get("temp", 0.0),
                       latitude=latitude,
                       longitude=longitude)

if __name__ == '__main__':
    lat = 19.4446544
    lon = -96.9543623
    import json
    weather = WeatherManager.instance().weather_from_lat_lon(latitude=lat, longitude=lon)
    print(json.dumps(weather, indent=4))
