from werkzeug.security import generate_password_hash

from . import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(256), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def commit(self):
        db.session.add(self)
        db.session.commit()
        user = type(self).query.filter_by(username=self.username).first()
        return user.id

    def exists(self):
        result = type(self).query.filter_by(username=self.username).first()
        return result is not None

    def check_password(self, password):
        hashed = generate_password_hash(password)
        if self.hashed_pw == hashed:
            return True
        return False
