from os import environ

from .core import create_app


app = create_app(secret_key=environ.get("IDIET_SECRET_KEY", "MY_SECRET"))
