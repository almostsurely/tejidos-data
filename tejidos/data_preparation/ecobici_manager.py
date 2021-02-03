from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import urllib.request
from functools import cache
from typing import Dict, Any

import pandas as pd
import requests

ECOBICI_CLIENT_ID = "ECOBICI_CLIENT_ID"
ECOBICI_CLIENT_SECRET = "ECOBICI_CLIENT_SECRET"
ECOBICI_ENDPOINT = "https://pubsbapi-latam.smartbike.com/oauth/v2"

ECOBICI_ENDPOINT_STATIONS = "https://pubsbapi-latam.smartbike.com/api/v1"


@dataclass
class AccessToken:
    client_id: str
    client_secret: str
    access_token: str
    expire_time: datetime
    refresh_token: str
    token_type: str
    scope: str = None

    @staticmethod
    def from_dict(d: Dict) -> AccessToken:
        return AccessToken(client_id=d.get("client_id"),
                           client_secret=d.get("client_secret"),
                           access_token=d.get("access_token"),
                           expire_time=datetime.now() + timedelta(seconds=int(d.get("expires_in"))),
                           refresh_token=d.get("refresh_token"),
                           scope=d.get("scope"),
                           token_type=d.get("token_type"))

    def is_fresh(self):
        return datetime.now() < self.expire_time

    def __eq__(self, other: AccessToken) -> bool:
        return self.client_id == other.client_id and \
               self.client_secret == other.client_secret and \
               self.access_token == other.access_token and \
               self.refresh_token == other.refresh_token and \
               self.scope == other.scope and \
               self.token_type == other.token_type



class EcobiciManager:
    _instance = None

    @classmethod
    def instance(cls) -> EcobiciManager:
        if cls._instance is None:
            client_id = os.getenv('ECOBICI_CLIENT_ID')
            client_secret = os.getenv('ECOBICI_CLIENT_SECRET')
            token = EcobiciManager.get_access_token(client_id=client_id, client_secret=client_secret)
            cls._instance = EcobiciManager(token=token)
        return cls._instance

    def __init__(self, token: AccessToken):
        self._token = token

    @property
    def _access_token(self):
        if not self._token.is_fresh():
            self.refresh_access_token()
        return self._token.access_token

    @staticmethod
    def get_access_token(client_id: str, client_secret: str) -> AccessToken:
        params = {"client_id": client_id,
                  "client_secret": client_secret,
                  "grant_type": "client_credentials"}

        access_data = EcobiciManager._call_endpoint(url=f'{ECOBICI_ENDPOINT}/token?{{params}}', params=params)

        return AccessToken.from_dict({**access_data, "client_id": client_id, "client_secret": client_secret})

    def refresh_access_token(self) -> AccessToken:
        params = {"client_id": self._token.client_id,
                  "client_secret": self._token.client_secret,
                  "grant_type": "refresh_token",
                  "refresh_token": self._token.refresh_token}

        logging.info("Refreshing token.")
        access_data = EcobiciManager._call_endpoint(url=f'{ECOBICI_ENDPOINT}/token?{{params}}', params=params)
        self._token = AccessToken.from_dict(access_data)

    @cache
    def get_station_list(self) -> Dict[str, Any]:
        print("calling get_station_list")
        params = {"access_token": self._access_token}
        return EcobiciManager._call_endpoint(url=f'{ECOBICI_ENDPOINT_STATIONS}/stations.json?{{params}}', params=params)

    def get_station_disponibility(self) -> Dict[str, Any]:
        print("calling get_station_disponibility")
        params = {"access_token": self._access_token}
        return EcobiciManager._call_endpoint(url=f'{ECOBICI_ENDPOINT_STATIONS}/stations/status.json?{{params}}',
                                             params=params)

    @staticmethod
    def _call_endpoint(url: str, params: Dict = None) -> Dict[str, Any]:
        params = params or {}
        gat_url = url.format(params=urllib.parse.urlencode(params))
        response = requests.get(gat_url)
        return response.json()


def main() -> None:
    ecobici_manager = EcobiciManager.instance()
    station_list = ecobici_manager.get_station_list()
    station_disponibility = ecobici_manager.get_station_disponibility()

    station_statuses = {}

    for status in station_disponibility['stationsStatus']:
        station_statuses.update({status.get("id"): status})

    result = []
    for station in station_list.get('stations', []):
        station_id = station.get('id')
        if station_id is not None:

            station_status = station_statuses.get(station_id, {})

            entry = {**station,
                     "lat": station.get("location", {}).get("lat"),
                     "lon": station.get("location", {}).get("lon"),
                     "available_bikes": station_status.get("availability", {}).get("bikes"),
                     "available_slots": station_status.get("availability", {}).get("slots"),
                     **station_status}

            del entry["location"]
            del entry["availability"]


            result.append(entry)


    ecobici_data = pd.DataFrame.from_dict(result)

    output_directory = 'data_ecobici'

    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    ecobici_data.to_csv(os.path.join(output_directory, 'ecobici_data.csv'), sep=',', encoding='utf-8')


if __name__ == "__main__":
    main()

