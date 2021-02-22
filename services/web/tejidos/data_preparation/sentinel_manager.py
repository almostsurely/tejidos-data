from __future__ import annotations

import logging
from typing import Tuple, List

from pandas import DataFrame
from sentinelsat import SentinelAPI
from datetime import date
from datetime import timedelta
import os
from os import path
from os.path import basename
from rasterio.mask import mask
import rasterio

SCIHUB_URL = 'https://scihub.copernicus.eu/dhus'
SCIHUB_USER = 'SCIHUB_USER'
SCIHUB_PASS = 'SCIHUB_PASS'


def timeframe(daysdelta: int = 10) -> Tuple[date]:
    start_date = date.today().replace(day=1) - timedelta(days=daysdelta)
    end_date = date.today()
    return start_date, end_date


def mask_from_json(geojson) -> List:
    return [geojson['features'][0]['geometry']]


def list_files(directory, endswith="60m.jp2"):
    files_endswith = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(endswith):
                fullpath = root + '/' + file
                files_endswith.append(fullpath)
    return files_endswith


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

    def api_query(self, footprint: str, begin_date: date, end_date: date, platformname: str = 'Sentinel-2',
                  cloudcoverpercentage: Tuple[int, int] = (0, 100)) -> DataFrame:
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

    def download_product(self, product: DataFrame, destination_path: str) -> str:
        """
        Checks if compressed product exists. If not, downloads it.
        :param product:
        :return: Name of file.
        """
        title = product['title'][0]
        product_name = os.path.join(destination_path, f"{title}.zip")
        if not path.exists(product_name):
            logging.info(f"Downloading {product_name}")
            self._sentinel_api.download_all(product.index, directory_path=destination_path)
        return product_name

    @staticmethod
    def harmonize_bands(directory: str, bands_list: List[str], cropping_mask: List, extension: str = "tif"):

        if not os.path.exists(directory):
            os.makedirs(directory)

        for band in bands_list:
            with rasterio.open(band) as src:
                out_image, out_transform = mask(src, cropping_mask, crop=True)

            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                             "height": out_image.shape[1],
                             "width": out_image.shape[2],
                             "transform": out_transform})
            output_path = basename(band)[:-4]
            with rasterio.open(os.path.join(directory, f"{output_path}.{extension}"), "w", **out_meta) as dest:
                dest.write(out_image)



if __name__ == '__main__':
    result = timeframe(15)
    _, last = timeframe(15)
    print(last)
