from __future__ import annotations
import argparse

import logging
import calendar
from typing import Tuple

import geojson
from pandas import DataFrame
from sentinelsat import SentinelAPI
from sentinelsat import read_geojson
from sentinelsat import geojson_to_wkt
from datetime import date
import os
from os import path
from zipfile import ZipFile

SCIHUB_URL = 'https://scihub.copernicus.eu/dhus'
SCIHUB_USER = 'SCIHUB_USER'
SCIHUB_PASS = 'SCIHUB_PASS'

class SentinelManager:

    _instance = None

    @classmethod
    def instance(cls) -> SentinelManager:
        if cls._instance is None:
            scihub_user = os.getenv(SCIHUB_USER)
            scihub_password = os.getenv(SCIHUB_PASS)
            sentinel_api = SentinelAPI(scihub_user, scihub_password, SCIHUB_URL)
            cls._instance = SentinelManager(sentinel_api=sentinel_api)
        return cls._instance

    def __init__(self, sentinel_api: SentinelAPI):
        self._sentinel_api = sentinel_api

    def api_query(self, footprint: str, begin_date: date, end_date: date, platformname: str='Sentinel-2', cloudcoverpercentage: Tuple[int, int]=(0, 100)) -> DataFrame:
        logging.info(f"Calling Sentinel api for images between {begin_date} and {end_date}.")
        query = self._sentinel_api.query(area=footprint,
                                         date=(begin_date, end_date),
                                         platformname=platformname,
                                         cloudcoverpercentage=cloudcoverpercentage)
        return self._sentinel_api.to_dataframe(query)

    @staticmethod
    def last_product(df) -> DataFrame:
        """
        Obtains most current product from a scihub query-dataframe.
        :param df:
        :return:
        """
        df_sorted = df.sort_values(['ingestiondate'], ascending=[False])
        df_sorted = df_sorted.head(1)
        return df_sorted

    def download_product(self, product: DataFrame) -> str:
        """
        Checks if compressed product exists. If not, downloads it.
        :param product:
        :return: Name of file.
        """
        product_name = str(product['title'][0]) + '.zip'
        if not path.exists(product_name):
            logging.info(f"Downloading {product_name}")
            self._sentinel_api.download_all(product.index)
        return product_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--footprint',
                        type=str,
                        default='data_polygons/roi_extent.geojson')
    parser.add_argument('--scihub-user',
                        type=str,
                        default=None)
    parser.add_argument('--scihub-password',
                        type=str,
                        default=None)

    arguments = parser.parse_args()

    if arguments.scihub_user is None or arguments.scihub_password is None:
        sentinel_manager = SentinelManager.instance()
    else:
        sentinel_manager = SentinelManager(sentinel_api=SentinelAPI(arguments.scihub_user,
                                                                    arguments.scihub_password,
                                                                    SCIHUB_URL))

    if os.path.isfile(arguments.footprint):
        footprint = geojson_to_wkt(read_geojson(arguments.footprint))
    else:
        # no footprint found, using simple geojson as example
        test_geojson = '{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-99.27108764648438, 19.230770079948247], [-99.01702880859374, 19.230770079948247], [-99.01702880859374, 19.54296671307226], [-99.27108764648438, 19.54296671307226], [-99.27108764648438, 19.230770079948247]]]}}]}'
        footprint = geojson_to_wkt(geojson.loads(test_geojson))

    today = date.today()
    year = today.year
    month = today.month

    first_day_current_month = date(year, month, 1)
    last_day_current_month = date(year, month, calendar.monthrange(year, month)[1])

    products = sentinel_manager.api_query(footprint=footprint,
                                          begin_date=first_day_current_month,
                                          end_date=last_day_current_month)

    product = SentinelManager.last_product(products)
    product_name = sentinel_manager.download_product(product)

    zipfile = ZipFile(product_name, 'r')
    zipfile.extractall('data_sentinel')
    zipfile.close()

    os.remove(product_name)


if __name__ == "__main__":
    main()
