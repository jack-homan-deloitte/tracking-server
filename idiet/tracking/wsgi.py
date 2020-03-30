import os

from flask_restful import Api
from flask import Flask

from .api import api
from .models import db


def create_app(**config):
    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        config[
            "SQLALCHEMY_DATABASE_URI"
        ] = os.environ["SQLALCHEMY_DATABASE_URI"]
    config.update({
        "SQLALCHEMY_TRACK_MODIFICATIONS": True
    })
    app = Flask(__name__)
    app.config.update(**config)
    api.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app
