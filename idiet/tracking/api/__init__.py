from flask import Response
from flask_restful import Resource, Api

from . import user


class HealthCheck(Resource):
    """
    endpoint to validate the api server can be reached

    Returns 200 response code
    """

    def get(self):
        return Response(status=200)


api = Api()
api.add_resource(HealthCheck, "/api/hc")
api.add_resource(user.CreateUser, "/api/user/create")
