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
from werkzeug.utils import secure_filename

from tejidos.extensions import db, Station, Shape, Sentinel
from tejidos.server.main.task import create_task, download_sentinel


def create_app(config: str):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

    return app

app = create_app("tejidos.config.Config")


@app.route("/")
def hello_world():
    stations = Station.query.all()
    images = Sentinel.query.all()
    return jsonify(shape=[{"name": sentinel.id,
                           "creation_date": sentinel.created_date} for sentinel in images])


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
    task = q.enqueue(download_sentinel)
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    return jsonify(response_object), 202
