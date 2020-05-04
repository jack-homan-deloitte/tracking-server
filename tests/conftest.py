import os

from hypothesis import settings
import pytest
import webtest

from idiet.tracking.core import create_app


settings.register_profile("debug", max_examples=1, deadline=None)
settings.register_profile("fast", max_examples=10, deadline=None)
settings.register_profile("slow", max_examples=100, deadline=300)
settings.register_profile("nightly", max_examples=1000, deadline=300)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "debug"))


@pytest.fixture
def test_app():
    config = {
        "secret-key": "MY_SECRET_KEY"
    }
    client = webtest.TestApp(create_app(config=config))
    return client
