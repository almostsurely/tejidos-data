import csv
import json
import os
import shutil
import time
import uuid

from os.path import basename
from typing import Dict, Union, List
from zipfile import ZipFile

import numpy as np
import pandas
import rasterio
from geoalchemy2.shape import to_shape
from flask import logging
from sentinelsat import read_geojson

from tejidos.ml.code.generate_textile_matrices_from_data import generate_textile_matrices_from_data
from tejidos.extensions import Shape, db, Sentinel, Loom
from tejidos.data_preparation.sentinel_manager import timeframe, SentinelManager, mask_from_json, list_files

def create_task(task_type: int) -> bool:
    time.sleep(int(task_type) * 10)
    return True

def create_pandas_file(directory: str, static_directory: str) -> str:
    raster_list = filter(lambda x: "TCI" not in x,
                         list_files(directory, endswith=".tif") + list_files(static_directory, endswith=".tif"))


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
    output_file = os.path.join(directory, f"{uuid.uuid4()}.csv")
    df_colonias.to_csv(output_file)
    return output_file


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
            product_name = SentinelManager.instance().download_product(product, "tejidos/media")
        zipfile = ZipFile(product_name, 'r')
        zipfile.extractall("tejidos/media")
        zipfile.close()
        mask = Shape.query.filter_by(name='mask').first()
        cropping_mask = mask_from_json(read_geojson('tejidos/static/roi_extent.json'))  # TODO: This mask should be ingested to the database, but it didn't like the projection.
        bands = list_files(f'tejidos/media/{basename(product_name)[:-4]}.SAFE')
        SentinelManager.harmonize_bands(f"tejidos/media/{title}", bands, cropping_mask)
        os.remove(product_name)
        shutil.rmtree(f'tejidos/media/{basename(product_name)[:-4]}.SAFE')
        db.session.add(Sentinel(id=title,
                                mask=mask))


        intermediate_result = create_pandas_file(f"tejidos/media/{title}", "tejidos/static")

        final_directory = f"tejidos/media/{title}/results"
        generate_textile_matrices_from_data(intermediate_result, final_directory)



        db.session.commit()
    return True


# if __name__ == '__main__':
#     intermediate_result = create_pandas_file("/Users/amaury/Development/tejidos-data/services/web/tejidos/media/S2B_MSIL2A_20210220T170329_N0214_R069_T14QMG_20210220T210147",
#                                 "/Users/amaury/Development/tejidos-data/services/web/tejidos/static")
#
#     generate_textile_matrices_from_data(intermediate_result, f"/Users/amaury/Development/tejidos-data/services/web/tejidos/media/S2B_MSIL2A_20210220T170329_N0214_R069_T14QMG_20210220T210147/result")
#
#     payload = csv_to_json_loom(f"/Users/amaury/Development/tejidos-data/services/web/tejidos/media/S2B_MSIL2A_20210220T170329_N0214_R069_T14QMG_20210220T210147/result")
#
#
#     print(json.dumps(payload))