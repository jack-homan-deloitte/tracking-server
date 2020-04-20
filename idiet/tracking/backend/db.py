from datetime import timedelta

import jwt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, REAL
from sqlalchemy.orm import sessionmaker, relationship

from idiet.tracking.backend.core import Backend
from idiet.tracking.timestamp import utcnow
from idiet.tracking.encrypt import hash_password, check_password_hash


Base = declarative_base()


class Token(Base):
    __tablename__ = "jwt_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True)
    expires_on = Column(Date, unique=False)

    def to_text(self):
        return self.token


class UserLogin(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    token = Column(String(256))
    profile = relationship("UserProfile", back_populates="user", uselist=False)

    def __eq__(self, other):
        return self.name == other.name

    def validate(self, password):
        return check_password_hash(self.token, password)

    def generate_token(self, secret):
        now = utcnow()
        exp = now + timedelta(hours=1)
        payload = {
            "user": self.name,
            "iat": now,
            "exp": exp
        }
        jwt_token = jwt.encode(payload, secret, algorithm="HS256")
        token = Token()
        token.expires_on = exp
        token.token = jwt_token.decode("utf-8")
        return token


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=True)
    gender = Column(String(16), nullable=True)
    member_since = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserLogin", back_populates="profile")

    def update(self, d):
        self.name = d.get("name", self.name)
        self.gender = d.get("gender", self.gender)

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "member_since": self.member_since,
        }


class FoodFact(Base):
    __tablename__ = "idietfoodtable"
    foodid = Column(Integer, primary_key=True)
    foodname = Column(Text, nullable=True)
    foodgroup = Column(Text, nullable=True)
    fatg = Column(REAL, nullable=True)
    proteing = Column(REAL, nullable=True)
    carbohydrateg = Column(REAL, nullable=True)
    calories = Column(REAL, nullable=True)

    def to_dict(self):
        return {
            "name": self.foodname,
            "group": self.foodgroup,
            "fat_in_grams": self.fatg,
            "protein_in_grams": self.proteing,
            "carbohydrates_in_grams": self.carbohydrateg,
            "calories": self.calories
        }

    @classmethod
    def from_dict(cls, d):
        food = cls()
        food.foodname = d.get("name", food.foodname)
        food.foodgroup = d.get("group", food.foodgroup)
        food.fatg = d.get("fat_in_grams", food.fatg)
        food.proteing = d.get("protein_in_grams", food.proteing)
        food.carbohydrateg = d.get(
            "carbohydrates_in_grams", food.carbohydrateg
        )
        food.calories = d.get("calories", food.calories)
        return food


class UserFoodItem(Base):
    __tablename__ = "user_meals"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=True)
    fat_in_grams = Column(Integer, nullable=True, default=0)
    carbs_in_grams = Column(Integer, nullable=True, default=0)
    protein_in_grams = Column(Integer, nullable=True, default=0)


class SqlAlchemyBackend(Backend):

    def __init__(self, engine, encryption_key=None):
        self.engine = engine
        self.encryption_key = encryption_key

    def init(self):
        Base.metadata.create_all(self.engine)
        return self

    def _create_session(self):
        return sessionmaker(bind=self.engine)()

    def add_user(self, username, password):
        session = self._create_session()
        password = hash_password(password)
        user = UserLogin(name=username, token=password)
        user.profile = UserProfile(member_since=utcnow())
        session.add(user)
        session.commit()
        return user

    user_add = add_user

    def get_user(self, username):
        session = self._create_session()
        user = session.query(UserLogin).filter_by(name=username).first()
        return user

    user_get = get_user

    def user_exists(self, username):
        user = self.get_user(username)
        return user is not None

    def user_validate(self, user, password):
        return user.validate(password)

    def user_generate_token(self, user, secret):
        return user.generate_token(secret)

    def user_profile_get(self, user):
        return user.profile

    def user_profile_update(self, user, post_data):
        profile = user.profile
        profile.update(post_data)
        session = self._create_session()
        result = session.query(UserProfile).filter_by(id=profile.id)
        result.update({UserProfile.name: post_data["name"],
                       UserProfile.gender: post_data["gender"]})
        session.commit()

    def user_from_token(self, token, secret):
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user = payload["user"]
        return self.user_get(user)

    def food_item_find_closest_match(self, name, max_results):
        session = self._create_session()
        # Check for exact match first
        food = session.query(FoodFact).filter_by(foodname=name).one_or_none()
        return [food.to_dict()]
