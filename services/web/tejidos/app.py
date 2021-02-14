

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

app = Flask(__name__)
app.config.from_object("tejidos.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

class Station(db.Model):
    __tablename__ = "station"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    address = db.Column(db.String(128), unique=True, nullable=False)
    geo = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    zip_code = db.Column(db.Integer)
    station_type = db.Column(db.String(128), nullable=False)

    def __init__(self, id: int, name: str, address: str, geo: str, zip_code: int, station_type: str):
        self.id = id
        self.name = name
        self.address = address
        self.geo = geo
        self.zip_code = zip_code
        self.station_type = station_type

@app.route("/")
def hello_world():
    stations = Station.query.all()
    return jsonify(stations=[{"id": station.id} for station in stations])