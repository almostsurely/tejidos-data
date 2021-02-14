from flask.cli import FlaskGroup

from tejidos.app import app, db, User, Station
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

        geo = 'SRID=4326;POINT({} {})'.format(station.get("location").get("lon"), station.get("location").get("lat"))
        db.session.add(Station(id=station.get("id"),
                               name=station.get("name"),
                               address=station.get("address"),
                               geo=geo,
                               zip_code=station.get("zipCode"),
                               station_type=station.get("stationType")))

    db.session.commit()

if __name__ == "__main__":
    cli()
