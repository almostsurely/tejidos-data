import os
from datetime import date

from flask import logging
from flask.cli import FlaskGroup
from geoalchemy2.shape import to_shape
from sentinelsat import read_geojson, geojson_to_wkt

from tejidos.data_preparation.sentinel_manager import timeframe, SentinelManager
from tejidos.app import app, db, User, Station, Shape
from tejidos.data_preparation.ecobici_manager import EcobiciManager

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("download_sentinel")
def download_sentinel_image():
    first_day_current_month = timeframe()[0]
    last_day_current_month = timeframe()[1]

    footprint = Shape.query.filter_by(name='cdmx').first()
    shply_geom = to_shape(footprint.geo)
    products = SentinelManager.instance().api_query(footprint=shply_geom.to_wkt(),
                                          begin_date=first_day_current_month,
                                          end_date=last_day_current_month)

    product = SentinelManager.last_product(products)
    SentinelManager.instance().download_product(product, "tejidos/static")


@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="michael@mherman.org"))

    ecobici_manager = EcobiciManager.instance()
    station_list = ecobici_manager.get_station_list()

    for station in station_list.get('stations', []):

        geo = 'POINT({} {})'.format(station.get("location").get("lon"), station.get("location").get("lat"))
        db.session.add(Station(id=station.get("id"),
                               name=station.get("name"),
                               address=station.get("address"),
                               geo=geo,
                               zip_code=station.get("zipCode"),
                               station_type=station.get("stationType")))

    source = os.path.join('tejidos/static', 'roi_extent_latlon.json')

    footprint = geojson_to_wkt(read_geojson(source))
    db.session.add(Shape(name="cdmx",
                         geo=footprint))



    db.session.commit()

if __name__ == "__main__":
    cli()
