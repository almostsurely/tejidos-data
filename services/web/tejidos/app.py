import json
import os

import geojson
from flask import Flask, jsonify, send_from_directory, request
from flask_crontab import Crontab
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object("tejidos.config.Config")
db = SQLAlchemy(app)
crontab = Crontab(app)


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
    geo = db.Column(Geometry(geometry_type='POINT'), nullable=False)
    zip_code = db.Column(db.Integer)
    station_type = db.Column(db.String(128), nullable=False)

    def __init__(self, id: int, name: str, address: str, geo: str, zip_code: int, station_type: str):
        self.id = id
        self.name = name
        self.address = address
        self.geo = geo
        self.zip_code = zip_code
        self.station_type = station_type


class Shape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    geo = db.Column(Geometry(geometry_type='POLYGON'), nullable=False)


@app.route("/")
def hello_world():
    stations = Station.query.all()
    shapes = Shape.query.all()
    return jsonify(stations=[{"id": station.id, "name": station.name, "zip": station.zip_code} for station in stations],
                   shape=[{"name": shape.name, "geo": geojson.loads(geojson.dumps(to_shape(shape.geo)))} for shape in shapes])


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return f"""
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """

@crontab.job(minute="1")
def my_scheduled_job():
    import time
    ts = time.time()
    with open(os.path.join(app.config["MEDIA_FOLDER"], f"{ts}.txt", "w")) as file:
        file.write(ts)
