import base64

from flask import Response, abort
from flask_restful import Resource, reqparse

from .. import models


def add_user(username, password, email):
    hashed = base64.b64encode(password.encode("utf-8"))
    user = models.User(username=username,
                       hashed_pw=hashed,
                       email=email)
    models.db.session.add(user)
    models.db.session.commit()
    user = models.User.query.filter_by(username=username).first()
    return user.id


def user_exists(username):
    user = models.User.query.filter_by(username=username).first()
    return user is not None


def parser_create_user():
    parser = reqparse.RequestParser()
    parser.add_argument("username", required=True,
                        type=str, help="user username")
    parser.add_argument("password", required=True,
                        type=str, help="password for user account")
    parser.add_argument("email", required=True, type=str, help="users email")
    args = parser.parse_args(strict=True)
    return args


class CreateUser(Resource):

    def put(self):
        """
        idempotent
        """
        args = parser_create_user()

        if not user_exists(args.username):
            add_user(args.username, args.password, args.email)

        return {"status": 200, "message": f"created user {args.username}"}

    def post(self):
        args = parser_create_user()

        if user_exists(args.username):
            abort(Response(
                f"User '{args.username}' already exists", status=403
            ))

        add_user(args.username, args.password, args.email)
        return Response(status=200)
