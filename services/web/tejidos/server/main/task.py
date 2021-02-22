import os
import shutil
import time
from os.path import basename
from zipfile import ZipFile

from geoalchemy2.shape import to_shape
from flask import logging
from sentinelsat import read_geojson

from tejidos.extensions import Shape, db, Sentinel
from tejidos.data_preparation.sentinel_manager import timeframe, SentinelManager, mask_from_json, list_files

def create_task(task_type: int) -> bool:
    time.sleep(int(task_type) * 10)
    return True

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
        db.session.commit()

    return True


if __name__ == '__main__':
    download_sentinel()