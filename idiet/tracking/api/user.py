import datetime

import attr
from flask import views, g, jsonify, make_response, request

from idiet.tracking.auth.views import auth
from idiet.tracking.core import api


@attr.s
class UserProfile(object):

    _profiles = {}

    first_name = attr.ib(factory=str)
    last_name = attr.ib(factory=str)
    date_of_birth = attr.ib(default=None)

    def as_dict(self):
        return attr.asdict(self)

    @classmethod
    def get(cls, user):
        user_profile = cls._profiles.get(user.id)
        return user_profile

    @classmethod
    def add(cls, profile, user):
        cls._profiles[user.id] = profile
        return profile


class UserProfileApi(views.MethodView):

    @auth.login_required
    def get(self):
        user = g.user
        profile = UserProfile.get(user)
        if profile:
            response = profile.as_dict()
        else:
            response = {}
        return make_response(jsonify(response), 200)

    @auth.login_required
    def post(self):
        user = g.user
        profile = UserProfile.get(user)
        post_data = request.get_json()

        first_name = post_data.get("first-name")
        last_name = post_data.get("last-name")
        date_of_birth = post_data.get("dob")

        profile = UserProfile(first_name=first_name, last_name=last_name,
                              date_of_birth=date_of_birth)
        UserProfile.add(profile, user)
        response = {
            "status": "success",
            "message": "information updated"
        }
        return make_response(jsonify(response), 200)


api.add_url_rule(
    "/user/profile",
    view_func=UserProfileApi.as_view("user_profile_api"),
    methods=["GET", "POST"]
)
