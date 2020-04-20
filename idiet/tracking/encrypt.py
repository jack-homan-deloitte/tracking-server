from datetime import timedelta

import jwt
from werkzeug import security

from idiet.tracking.timestamp import utcnow


def hash_password(password):
    return security.generate_password_hash(password, salt_length=10)


def check_password_hash(password_hash, password):
    return security.check_password_hash(password_hash, password)


def jwt_encode(user, secret, **jwt_args):
    now = utcnow()
    payload = {
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": user
    }
    return jwt.encode(payload, secret, algorithm="HS256", **jwt_args)


def jwt_decode(user, secret, **jwt_args):
    payload = jwt.decode(secret, algorithms=['HS256'])
    return jwt.encode(payload, secret, **jwt_args)
