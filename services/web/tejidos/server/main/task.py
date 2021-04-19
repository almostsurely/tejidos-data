import csv
import json
import os
import shutil
import time
import uuid
from math import atan2, sin, cos, radians, sqrt

from os.path import basename
from typing import Dict, Union, List
from zipfile import ZipFile

import numpy as np
import pandas
import rasterio
from geoalchemy2.shape import to_shape
import logging

from sentinelsat import read_geojson
from sklearn.neighbors import KNeighborsRegressor

from tejidos.data_preparation.ecobici_manager import EcobiciManager
from tejidos.data_preparation.twitter_manager import TwitterManager, Earthquake
from tejidos.data_preparation.weather_manager import Weather, WeatherManager
from tejidos.ml.code.generate_textile_matrices_from_data import generate_textile_matrices_from_data
from tejidos.extensions import Shape, db, Sentinel, Loom
from tejidos.data_preparation.sentinel_manager import timeframe, SentinelManager, mask_from_json, list_files


def create_task(task_type: int) -> bool:
    time.sleep(int(task_type) * 10)
    return True


def create_pandas_file(directory: str, static_directory: str) -> str:
    raster_list = filter(lambda x: "TCI" not in x,
                         list(np.random.choice(list_files(directory, endswith=".tif"), 5)) + list_files(static_directory, endswith=".tif"))

    column_names = []
    result = []
    for raster in raster_list:
        with rasterio.open(raster, 'r') as ds:
            column_names.append(basename(os.path.splitext(raster)[0]))
            read = ds.read().flatten()
            print(f"{read.shape}:{raster}")
            result.append(read)
    brick = np.vstack(result).transpose()

    group_by_column = next(filter(lambda x: 'colonias' in x, column_names))

    df = pandas.DataFrame(data=brick, index=np.arange(brick.shape[0]), columns=column_names)
    df_colonias = df.groupby([group_by_column]).mean()

    earthquakes = TwitterManager.instance().fetch_earthquake(number=1)

    if len(earthquakes):
        latest_earthquake = earthquakes[0]
        df_colonias['earthquake_magnitude'] = df_colonias.apply(magnitude_factory(latest_earthquake), axis=1)

    weather_grid = WeatherManager.instance().get_weather_cdmx()

    X = []
    y = []
    for weather in weather_grid:

        X.append([weather.latitude, weather.longitude])
        y.append([weather.humidity, weather.temp, weather.wind_speed])

    knn_model = KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn_model.fit(X=X, y=y)

    df_colonias['weather_humidity_intensity'] = df_colonias.apply(weather_factory(model=knn_model, column=0), axis=1)
    df_colonias['weather_wind_speed_intensity'] = df_colonias.apply(weather_factory(model=knn_model, column=1), axis=1)
    df_colonias['weather_temp_intensity'] = df_colonias.apply(weather_factory(model=knn_model, column=2), axis=1)

    ecobicis = EcobiciManager.instance().get_all()

    X_ecobicies = []
    y_ecobicies = []
    for ecobici in ecobicis:
        X_ecobicies.append([ecobici.latitude, ecobici.longitude])
        y_ecobicies.append([ecobici.available_bikes])

    knn_model.fit(X=X_ecobicies, y=y_ecobicies)

    df_colonias['ecobicis_availability'] = df_colonias.apply(weather_factory(model=knn_model, column=0), axis=1)

    output_file = os.path.join(directory, f"{uuid.uuid4()}.csv")
    df_colonias.to_csv(output_file)
    return output_file


def magnitude_factory(earthquake: Earthquake) -> float:
    def magnitude(row) -> float:
        return earthquake.magnitude / distance_lat_lon(row['5_lat'], row['5_lon'], earthquake.latitude,
                                                       earthquake.longitude) ** 2
    return magnitude


def weather_factory(model: KNeighborsRegressor, column: int) -> float:
    def intensity(row) -> float:
        return model.predict([[row['5_lat'], row['5_lon']]])[0][column]
    return intensity


def distance_lat_lon(lat_1: float, lon_1: float, lat_2: float, lon_2: float) -> float:
    R = 6373.0
    lat1 = radians(lat_1)
    lon1 = radians(lon_1)
    lat2 = radians(lat_2)
    lon2 = radians(lon_2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))



def csv_to_json_loom(directory: str) -> Dict:
    csv_files = list_files(directory, endswith=".csv")

    def transform(data: Union[List, str]) -> Union[List, int]:
        if isinstance(data, list):
            return [transform(element) for element in data]
        return int(float(data))

    result = {}
    for csv_file in csv_files:
        with open(csv_file, 'r') as csv_file_handle:
            data_loaded = list(csv.reader(csv_file_handle, delimiter=','))
            result.update({basename(os.path.splitext(csv_file)[0]): transform(data_loaded)})
    return result


def download_sentinel() -> bool:
    first_day_current_month = timeframe()[0]
    last_day_current_month = timeframe()[1]
    footprint = Shape.query.filter_by(name='cdmx').first()
    shaply_geom = to_shape(footprint.geo)
    products = SentinelManager.instance().api_query(footprint=shaply_geom.to_wkt(),
                                                    begin_date=first_day_current_month,
                                                    end_date=last_day_current_month)
    product = SentinelManager.last_product(products)
    title = product['title'][0]

    if not Sentinel.query.filter_by(id=title).count() > 0:
        product_name = os.path.isfile(os.path.join("tejidos/media", f"{title}.zip"))
        if not os.path.isfile(product_name):
            print("Downloading product.")
            product_name = SentinelManager.instance().download_product(product, "tejidos/media")
        zipfile = ZipFile(product_name, 'r')
        print("Extracting zip file.")
        zipfile.extractall("tejidos/media")
        zipfile.close()
        mask = Shape.query.filter_by(name='mask').first()
        cropping_mask = mask_from_json(read_geojson(
            'tejidos/static/roi_extent.json'))  # TODO: This mask should be ingested to the database, but it didn't like the projection.
        bands = list_files(f'tejidos/media/{basename(product_name)[:-4]}.SAFE')
        logging.info("Harmonizing.")
        SentinelManager.harmonize_bands(f"tejidos/media/{title}", bands, cropping_mask)
        os.remove(product_name)
        shutil.rmtree(f'tejidos/media/{basename(product_name)[:-4]}.SAFE')
        db.session.add(Sentinel(id=title,
                                mask=mask))
        intermediate_result = create_pandas_file(f"tejidos/media/{title}", "tejidos/static")
        final_directory = f"tejidos/media/{title}/results"
        print("Generating textile matrices.")
        generate_textile_matrices_from_data(intermediate_result, final_directory)
        db.session.commit()
    return True


if __name__ == '__main__':
    sentinel_id = 'S2A_MSIL2A_20210416T165851_N0300_R069_T14QMG_20210416T222158'
    create_pandas_file(f"/Users/amaury/Development/tejidos-data/services/web/tejidos/media/{sentinel_id}",
                       "/Users/amaury/Development/tejidos-data/services/web/tejidos/static")
