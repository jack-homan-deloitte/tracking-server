from string import ascii_letters

from hypothesis import strategies as st, given, assume
import pytest
from sqlalchemy import create_engine

from idiet.tracking.backend.db import SqlAlchemyBackend


def alchemy():
    engine = create_engine("sqlite://")
    backend = SqlAlchemyBackend(engine)
    backend.init()
    return backend


@pytest.fixture(params=[alchemy], scope="session")
def backend(request):
    return request.param()


class TestBackend:

    @given(
        username=st.emails(),
        password=st.text(min_size=8, alphabet=ascii_letters)
    )
    def test_add_and_get_user(self, backend, username, password):

        assume(backend.user_exists(username) is False)
        user = backend.add_user(username, password)
        assert user.name == username
        assert user.token != password
        assert backend.get_user(username) == user
