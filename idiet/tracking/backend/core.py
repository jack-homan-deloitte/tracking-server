import abc
import jwt
from datetime import datetime


def encode(uname, password, **jwt_args):
    payload = {
        "aud": uname,
        "iat": datetime.utcnow(),
    }
    encoded = jwt.encode(payload, password, algorithm="HS256")
    return encoded


def decode(token, password, **jwt_args):
    payload = jwt.decode(token, password, algorithm="HS256")
    return payload


class UserLogin(abc.ABC):
    """
    stores user login information needed to authenticate
    with the tracking server

    Methods
    -------
    track:
        encrypt user chosen password and store email and password
        in the backend. Not, all user information will be access by jwt
        token not by anything identifiable.
    """

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def token(self):
        pass

    def __eq__(self, other):
        return self.name == other.name and self.token == other.token


class Backend(abc.ABC):
    """
    app metadata store

    The backend storage could be a database, a filesystem, or an in memory
    file system depending on the implementation. Backend provides a way
    to create manager user activity such as counting a meal, token auth, user
    profiles etc
    """

    def register_user(self, user):
        pass

    def create_user_profile(self, user):
        pass
