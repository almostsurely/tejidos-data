import json
import os

import geojson
import redis
import rq_dashboard
from flask import Flask, jsonify, send_from_directory, request, current_app
from flask_crontab import Crontab
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from redis import Connection
from rq import Queue
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from tejidos.data_preparation.twitter_manager import TwitterManager
from tejidos.data_preparation.weather_manager import WeatherManager
from tejidos.extensions import db, Station, Shape, Sentinel, Loom
from tejidos.server.main.task import create_task, download_sentinel, csv_to_json_loom, dowload_and_process_sentinel


def create_app(config: str):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    return app

app = create_app("tejidos.config.Config")


@app.route("/satellite")
def satellite():
    include_draft = request.args.get('include_draft', default=0, type=int)
    print(f"include_draft {include_draft}")
    sentinel = Sentinel.query.order_by(desc(Sentinel.created_date)).first()
    sentinel_id = sentinel.id
    loom_result_json = csv_to_json_loom(f"tejidos/media/{sentinel_id}/results", exclude_draft=include_draft == 0)
    return jsonify(payload=loom_result_json, date=sentinel.created_date)

@app.route("/earthquakes")
def earthquakes():
    return jsonify(payload=TwitterManager.instance().fetch_earthquake(number=10))

@app.route("/weather")
def weather():
    return jsonify(payload=WeatherManager.instance().weather_from_lat_lon(latitude=os.getenv("THE_SUMMIT_LATITUDE"),
                                                                          longitude=os.getenv("THE_SUMMIT_LONGITUDE")))

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


@app.route("/tasks", methods=["POST"])
def run_task():
    task_type = request.json["type"]
    q = Queue(connection=redis.from_url(current_app.config["REDIS_URL"]),
              default_timeout=current_app.config["REDIS_TIMEOUT"])
    task = q.enqueue(create_task, task_type)
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    return jsonify(response_object), 202


@app.route("/sentinel", methods=["POST"])
def download_sentinel_handler():
    q = Queue(connection=redis.from_url(current_app.config["REDIS_URL"]),
              default_timeout=current_app.config["REDIS_TIMEOUT"])
    task = q.enqueue(dowload_and_process_sentinel)
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    return jsonify(response_object), 202


if __name__ == '__main__':

    sentinel_id = 'S2A_MSIL2A_20210416T165851_N0300_R069_T14QMG_20210416T222158'
    loom_result_json = csv_to_json_loom(f"/Users/amaury/Development/tejidos-data/services/web/tejidos/media/{sentinel_id}/results")
    print(loom_result_json)
