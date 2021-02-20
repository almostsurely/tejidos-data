import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/tejidos/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/tejidos/media"
    WTF_CSRF_ENABLED = True
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_TIMEOUT = 600
    QUEUES = ["default"]
