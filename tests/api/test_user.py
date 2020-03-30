import pytest
import webtest

from idiet.tracking.wsgi import create_app


@pytest.fixture
def test_app():
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    }
    app = create_app(**config)
    client = webtest.TestApp(app)
    return client


class TestCreateUser(object):

    def test_create_user_put(self, test_app):
        params = {
            "username":  "tomhanks",
            "email": "tom.hanks@gmail.com",
            "password": "pa$$w0rd"
        }

        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200

    def test_create_user_put_idempotent(self, test_app):
        params = {
            "username":  "tomhanks",
            "email": "tom.hanks@gmail.com",
            "password": "pa$$w0rd"
        }

        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200
        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200
        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200
        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200
        resp = test_app.put_json("/api/user/create", params)
        assert resp.status_int == 200

    def test_create_user_returns_invalid_when_missing_args(self, test_app):
        params = {
            "username":  "tomhanks",
            "email": "tom.hanks@gmail.com",
        }

        resp = test_app.put_json("/api/user/create", params, status=400)
        assert resp.status_int == 400

    def test_create_user_post(self, test_app):
        params = {
            "username":  "tomhanks",
            "email": "tom.hanks@gmail.com",
            "password": "pa$$w0rd"
        }

        resp = test_app.post_json("/api/user/create", params, status=200)
        resp = test_app.post_json("/api/user/create", params, status=403)
        assert resp.status_code == 403


class TestGetUser(object):

    def test_get_user(self, test_app):
        pass
