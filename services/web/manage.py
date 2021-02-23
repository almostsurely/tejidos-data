import os
from datetime import date

import redis
from flask import logging
from flask.cli import FlaskGroup
from rq import Worker
from sentinelsat import read_geojson, geojson_to_wkt
from tejidos.extensions import app, db, User, Station, Shape
from tejidos.data_preparation.ecobici_manager import EcobiciManager

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


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

    shapes = {'cdmx': 'roi_extent_latlon.json'}

    for name, filename in shapes.items():
        source = os.path.join('tejidos/static', filename)
        footprint = geojson_to_wkt(read_geojson(source))
        db.session.add(Shape(name=name,
                             geo=footprint))

    db.session.commit()

@cli.command("run_worker")
def run_worker():
    redis_url = app.config["REDIS_URL"]
    redis_connection = redis.from_url(redis_url)
    worker = Worker(app.config["QUEUES"], connection=redis_connection)
    worker.work()


if __name__ == "__main__":
    cli()
