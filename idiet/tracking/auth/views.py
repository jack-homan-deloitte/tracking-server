import base64
import datetime
import os

import attr
import jwt
from flask import request, make_response, jsonify, url_for, Blueprint, g
from flask.views import MethodView
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import generate_password_hash


auth_bp = Blueprint("auth", __name__)
auth = HTTPTokenAuth(scheme="Bearer")



def get_secret(key=os.urandom(16)):
    return key


class Token(object):

    _tokens = {}

    def __init__(self, user):
        pass

    @classmethod
    def add(cls, token, user):
        cls._tokens[token] = user
        return token

    @classmethod
    def delete(cls, token):
        del cls._token[token]
        return token
    
    @classmethod
    def user_from_token(cls, token):
        user = cls._tokens.get(token)
        return user


class User(object):

    _users = {}

    def __init__(self, email, password, unique_id):
        self.email = email
        self.password = password
        self.id = unique_id

    def auth_token(self):
        user_id = self.id
        now = datetime.datetime.utcnow()
        payload = {
            "aud": self.id,
            "iat": now,
            "exp": now + datetime.timedelta(days=0, hours=1)
        }
        encoded = jwt.encode(payload, get_secret(), algorithm="HS256")
        Token.add(encoded, self)
        return encoded

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, get_secret(), algorithm="HS256")
        except jwt.ExpiredSignatureError:
            # I think I probably don't need this
            # time > payload["exp"]
            return False
        except jwt.InvalidTokenError:
            # can't decode
            return False
        return True

    @classmethod
    def create(cls, email, password):
        unique = int(base64.b16encode(email.encode("utf-8")), 16)
        hashed = generate_password_hash(password)
        return cls(email, hashed, unique)

    @classmethod
    def add(cls, user):
        cls._users[user.id] = user
        return user

    @classmethod
    def delete(cls, user):
        del cls._users[user.id]
        return user

    @classmethod
    def get(cls, email, password):
        user = cls.create(email, password)
        if user.id in cls._users:
            return user
        return None


def get_secret():
    return "MY_SECRET_KEY"


class RegisterApi(MethodView):
    def post(self):
        """
        create a user with params user, password
        """
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        user = User.get(email, password)
        if user:
            response = {
                "status": "fail",
                "message": "User already exists"
            }
            return make_response(jsonify(response), 202)
        else:
            user = User.create(email, password)
            User.add(user)
            auth_token = user.auth_token()
            response = {
                "status": "success",
                "message": "sucessfully registered",
                "auth_token": auth_token.decode()
            }
            return make_response(jsonify(response), 201)


class LoginApi(MethodView):
    def post(self):
        """
        login a user with params user, password and return a
        auth_token
        """
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("email")
        user = User.get(email, password)
        if user:
            auth_token = user.auth_token()
            response = {
                "status": "success",
                "message": "login successful",
                "auth_token": auth_token.decode()
            }
            return make_response(jsonify(response), 201)
        response = {
            "status": "failed",
            "message": "User does not exist",
        }
        return make_response(jsonify(response), 401)


@auth.verify_token
def verify_token(token):
    user = Token.user_from_token(token.encode("utf-8"))
    g.user = user
    return g.user is not None


auth_bp.add_url_rule(
    "/auth/register",
    view_func=RegisterApi.as_view("registration_api"),
    methods=["POST"]
)
auth_bp.add_url_rule(
    "/auth/login",
    view_func=LoginApi.as_view("login_api"),
    methods=["POST"]
)
