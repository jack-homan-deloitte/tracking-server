
from hypothesis import given, strategies as st
import webtest

from idiet.tracking.core import create_app


def _create_app():
    app = create_app()
    test_app = webtest.TestApp(app)
    return test_app


class _Patch(object):
    def setup_example(self):
        from idiet.tracking.auth.views import User
        from idiet.tracking.api.user import UserProfile
        User._users = {}
        UserProfile._profiles = {}

    def register_user(self, app, email, password):
        response = app.post_json("/auth/register", {
            "email": email, "password": password
        }, status=201)
        token = response.json["auth_token"]
        return token


class TestUserProfileApi(_Patch):

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_get_user(self, app, email, password):
        token = self.register_user(app, email, password)
        headers = {
            "Authorization": f"Bearer {token}"
        }

        profile = app.get("/api/user/profile", headers=headers)
        assert profile.status_code == 200
        assert profile.json == {}

    @given(app=st.builds(_create_app), email=st.emails(), password=st.text())
    def test_get_user_can_post_info(self, app, email, password):
        token = self.register_user(app, email, password)
        headers = {
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "first-name": "Jack",
            "last-name": "Homan",
            "dob": "1990-12-17"
        }
        response = app.post_json("/api/user/profile", payload, headers=headers)
        assert response.json["status"] == "success"
        
