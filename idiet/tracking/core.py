import os

from flask import Flask
from flask import Blueprint, g, current_app, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import create_engine

from idiet.tracking.backend.db import SqlAlchemyBackend


token_auth = HTTPTokenAuth(scheme="Bearer")


class Tracking(Flask):

    def __init__(self, backend=None, config=None, secret_key=None,
                 *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self.backend = backend
        self.app_config = config
        self.secret_key = secret_key


app = Blueprint("app", __name__)
api = Blueprint("api", __name__)


@token_auth.verify_token
def verify_token(token):
    backend = current_app.backend
    secret_key = current_app.secret_key
    user = backend.user_from_token(token, secret_key)
    if user:
        g.user = user
        return True
    return False


@api.route("/api/hc")
def hc():
    return make_response(jsonify({"status": "success"}), 200)


def create_app(config=None, backend=None, secret_key=None):
    if backend is None:
        engine = create_engine("sqlite://")
        backend = SqlAlchemyBackend(engine)
        backend.init()
    if config and config.get("secret-key") == "":
        raise ValueError("Cannot create app without encryption key")
    app = Tracking(backend=backend, config=(config or {}),
                   secret_key=secret_key)
    import idiet.tracking.api  # noqa: F401
    app.register_blueprint(api)
    CORS(app)
    return app
