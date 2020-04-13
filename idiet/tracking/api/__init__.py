from flask import jsonify, make_response

from . import user
from ..core import api


@api.route("/hc", methods=["GET"])
def hc():
    response = jsonify({
        "message": "heathly"
    })
    return make_response(response, 200)
