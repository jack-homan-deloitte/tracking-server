import os

from hypothesis import settings
import pytest
import webtest

from idiet.tracking.core import create_app, Config


settings.register_profile("debug", max_examples=1, deadline=None)
settings.register_profile("local", max_examples=10, deadline=None)
settings.register_profile("github", max_examples=1000, deadline=None)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "local"))


@pytest.fixture
def test_app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    client = webtest.TestApp(create_app())
    return client
