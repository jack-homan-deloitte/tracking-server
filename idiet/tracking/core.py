from os import environ

from flask import Flask, Blueprint, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth

from .auth import auth_bp


api = Blueprint("api", __name__, url_prefix="/api")
db = SQLAlchemy()
auth = HTTPTokenAuth(scheme="token")


class Config:
     TESTING = environ.get('TESTING')
     FLASK_DEBUG = environ.get('FLASK_DEBUG')
     SECRET_KEY = environ.get('SECRET_KEY', "MY_SECRET_KEY_IS")
     # Database
     SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
     SQLALCHEMY_TRACK_MODIFICATIONS = environ.get(
         'SQLALCHEMY_TRACK_MODIFICATIONS', False
     )


@api.before_request
def before_request():
    if request.path in ("/api/user/create", "/api/hc"):
        # bypass create and health check
        return


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    import idiet.tracking.api
    app.register_blueprint(api)
    app.register_blueprint(auth_bp)
    CORS(app)
    return app
