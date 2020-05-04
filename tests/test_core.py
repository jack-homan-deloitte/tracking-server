import pytest

from idiet.tracking.core import create_app
from idiet.tracking.backend.db import SqlAlchemyBackend


class TestTracking(object):

    def test_create_app(self):
        """
        create application with default db backend
        """

        app = create_app(config={})
        assert type(app.backend) == SqlAlchemyBackend

    def test_create_app_with_config(self):
        """
        create app with config parameters
        """

        config = {
            "secret-key": "my-secret-key"
        }

        app = create_app(config=config)
        assert app.app_config["secret-key"] == "my-secret-key"

    def test_create_app_fails_when_missing_key(self):

        config = {
            "secret-key": ""
        }
       with pytest.raises(ValueError): 
            app = create_app(config=config)
