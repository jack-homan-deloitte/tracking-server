from datetime import timedelta
from functools import partial

from faker import Faker
from hypothesis import assume, given, settings, strategies as st
import pytest
import webtest
from idiet.tracking.core import create_app


def _create_app():
    app = create_app()
    test_app = webtest.TestApp(app)
    return test_app


class PatchUser(object):
    def setup_example(self):
        # TODO: Patch to make tests works
        from idiet.tracking.auth.views import User  # Delete this later
        User._users = {}


class TestRegisterApi(PatchUser):

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_register_user_response_success(self, app, **payload):
        response = app.post_json("/auth/register", payload, status=201)
        assert response.json["status"] == "success"

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_register_returns_auth_token(self, app, **payload):
        response = app.post_json("/auth/register", payload, status=201)
        assert response.json.get("auth_token")

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_register_user_user_exists(self, app, **payload):
        response = app.post_json("/auth/register", payload, status=201)
        assert response.status_code == 201
        response = app.post_json("/auth/register", payload, status=202)
        assert response.status_code == 202
        assert response.json["status"].startswith("fail")


class TestLoginApi(PatchUser):

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_login_user_does_not_exist(self, app, email, password):
        payload = {
            "email": email,
            "password": password
        }
        assume(password)
        response = app.post_json("/auth/login", payload, status=401)
        assert response.json.get("status").startswith("fail")

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_login_user_exists(self, app, email, password):
        assume(password)

        payload = {
            "email": email,
            "password": password
        }
        response = app.post_json("/auth/register", payload, status=201)
        response = app.post_json("/auth/login", payload, status=201)
        assert response.json.get("status") == "success"
        assert response.json.get("auth_token")
