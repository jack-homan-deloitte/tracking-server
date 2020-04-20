from flask import current_app, g, request, make_response, jsonify
from flask.views import MethodView

from idiet.tracking.core import api, token_auth
from idiet.tracking.timestamp import utcnow


class RegisterView(MethodView):

    def post(self):
        backend = current_app.backend

        request_json = request.get_json()
        uname = request_json["username"]
        password = request_json["password"]

        user = backend.get_user(uname)
        if not user:
            user = backend.add_user(uname, password)
            response = {
                "status": "success",
                "message": "create new user",
                "timestamp": str(user.profile.member_since)
            }
            return make_response(jsonify(response), 201)
        response = {
            "status": "failed",
            "message": "user already exists",
        }
        return make_response(jsonify(response), 302)


class LoginView(MethodView):

    def post(self):
        backend = current_app.backend
        secret_key = current_app.secret_key

        request_json = request.get_json()
        uname = request_json["username"]
        password = request_json["password"]

        if backend.user_exists(uname):
            user = backend.get_user(uname)
            if user.validate(password):
                token = user.generate_token(secret_key)
                response = {
                    "status": "success",
                    "message": "created user auth token",
                    "expires_on": str(token.expires_on),
                    "token": token.to_text()
                }
                return make_response(jsonify(response), 202)
            else:
                response = {
                    "status": "failed",
                    "message": "Could not authenticate user",
                }
                return make_response(jsonify(response), 401)
        else:
            response = {
                "status": "failed",
                "message": "user does not exist"
            }
            return make_response(jsonify(response), 403)


class UserProfileView(MethodView):

    @token_auth.login_required
    def get(self):
        backend = current_app.backend

        profile = backend.user_profile_get(g.user)
        data = profile.to_dict()
        response = {
            "message": "success",
            "ts": utcnow(),
            "data": data
        }
        return make_response(jsonify(response), 202)

    @token_auth.login_required
    def post(self):
        backend = current_app.backend

        post_data = request.get_json()
        try:
            backend.user_profile_update(g.user, post_data)
        except KeyError:
            response = {
                "status": "failed",
                "message": f"Invalid data"
            }
            return make_response(jsonify(response), 304)
        response = {
            "status": "success",
            "message": f"updated values {', '.join(post_data.keys())}"
        }
        return make_response(jsonify(response), 202)


@api.route("/api/food/search", methods=["GET"])
@token_auth.login_required
def food_search():
    backend = current_app.backend
    request_params = dict(request.args)
    try:
        request_params["name"]
    except KeyError:
        response = {
            "status": "failed",
            "message": "Invalid request. Search requires parameter 'name'"
        }
        return make_response(jsonify(response), 400)
    max_results = request_params.get("max_results", 10)
    items = backend.food_item_find_closest_match(request_params["name"],
                                                 max_results=max_results)
    n_items = len(items)
    response = {
        "status": "success",
        "message": f"{n_items} results found",
        "num_results": n_items,
        "data": items
    }
    return make_response(jsonify(response), 202)


register_view = RegisterView.as_view("registration_api")
login_view = LoginView.as_view("login_api")
user_profile_view = UserProfileView.as_view("profile_api")

api.add_url_rule("/api/register", view_func=register_view)
api.add_url_rule("/api/login", view_func=login_view)
api.add_url_rule("/api/user/profile", view_func=user_profile_view)
