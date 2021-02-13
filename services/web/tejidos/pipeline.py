import os
from datetime import date
from os.path import basename
from zipfile import ZipFile

import argparse
import geojson
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

from tejidos import SentinelManager, SCIHUB_URL, timeframe, mask_from_json, list_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--footprint',
                        type=str,
                        default='data_preparation/data_polygons/roi_extent_latlon.json')
    parser.add_argument('--mask',
                        type=str,
                        default='data_preparation/data_polygons/roi_extent.json')
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

    first_day_current_month = timeframe()[0]
    last_day_current_month = timeframe()[1]

    products = sentinel_manager.api_query(footprint=footprint,
                                          begin_date=first_day_current_month,
                                          end_date=last_day_current_month)

    product = SentinelManager.last_product(products)
    product_name = sentinel_manager.download_product(product, "")


    #"LATEST.ZIP"

    #"S2A_MSIL2A_20210126T170601_N0214_R069_T14QMG_20210203T194426.ZIP"
    #"S2A_MSIL2A_20210126T170601_N0214_R069_T14QMG_20210126T194426.ZIP"

    zipfile = ZipFile(product_name, 'r')
    zipfile.extractall('data_sentinel')
    zipfile.close()

    cropping_mask = mask_from_json(read_geojson(arguments.mask))

    bands = list_files('data_sentinel/' + basename(product_name)[:-4] + ".SAFE")

    SentinelManager.harmonize_bands(bands, cropping_mask)

    os.remove(product_name)








if __name__ == "__main__":
    main()