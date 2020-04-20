from string import ascii_letters
import random
import re

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hypothesis import strategies as st, given, settings
import webtest

from idiet.tracking.core import create_app
from idiet.tracking.backend.db import SqlAlchemyBackend, FoodFact


def fullname():
    faker = Faker()
    first = random.choice([
        faker.first_name,
        faker.first_name_female,
        faker.first_name_male,
        str
    ])
    last = random.choice([
        faker.last_name,
        faker.last_name_male,
        faker.last_name_female,
        faker.name,  # middle and last
        str
    ])

    prefix = random.choice([faker.prefix, str])
    suffix = random.choice([
        faker.suffix,
        faker.suffix_male,
        faker.suffix_female,
        str, str, str, str, str
    ])
    name = " ".join((prefix(), first(), last(), suffix()))
    return re.sub(f" {2}", " ", name)


class TestRegisterView(object):

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_register_user(self, username, password):
        app = webtest.TestApp(create_app())

        post_data = {"username": username, "password": password}
        response = app.post_json("/api/register", post_data)
        assert response.status_code == 201
        assert response.json["status"] == "success"

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_register_user_twice(self, username, password):
        backend = SqlAlchemyBackend(create_engine("sqlite://"))
        backend.init()
        app = webtest.TestApp(create_app(backend=backend))

        post_data = {"username": username, "password": password}
        response = app.post_json("/api/register", post_data)
        assert response.status_code == 201
        assert response.json["status"] == "success"

        post_data = {"username": username, "password": password}
        response = app.post_json("/api/register", post_data)
        assert response.status_code == 302
        assert response.json["status"] == "failed"


class TestLoginView(object):

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_user_can_get_token(self, username, password):
        app = webtest.TestApp(create_app(secret_key="key"))
        post_data = {"username": username, "password": password}
        app.post_json("/api/register", post_data)

        response = app.post_json("/api/login", post_data)
        assert "token" in response.json
        assert response.status_code == 202

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_user_cannot_get_token_if_dne(self, username, password):
        app = webtest.TestApp(create_app(secret_key="key"))

        post_data = {"username": username, "password": password}
        response = app.post_json("/api/login", post_data, status=403)
        assert response.json["status"] == "failed"
        assert response.status_code == 403

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_user_cannot_login_with_wrong_password(self, username, password):
        app = webtest.TestApp(create_app(secret_key="key"))
        post_data = {"username": username, "password": password}
        app.post_json("/api/register", post_data)

        post_data = {"username": username, "password": password + "suffix"}
        response = app.post_json("/api/login", post_data, status=401)
        assert "token" not in response.json
        assert response.status_code == 401
        assert response.json["status"] == "failed"


class TestUserProfileView(object):

    @given(username=st.emails(), password=st.text(alphabet=ascii_letters))
    def test_get(self, username, password):
        app = webtest.TestApp(create_app(secret_key="key"))
        post_data = {"username": username, "password": password}
        app.post_json("/api/register", post_data)

        response = app.post_json("/api/login", post_data)
        token = response.json["token"]

        headers = {
            "Authorization": f"Bearer {token}",
            "ContentType": "Application/json"
        }
        response = app.get("/api/user/profile", headers=headers)
        data = response.json["data"]
        assert data["member_since"]
        assert not data["name"]
        assert not data["gender"]

    @given(
        username=st.emails(),
        password=st.text(alphabet=ascii_letters),
        gender=st.builds(lambda: random.choice(["male", "female", "other"])),
        name=st.builds(fullname)
    )
    def test_post(self, username, password, gender, name):
        app = webtest.TestApp(create_app(secret_key="key"))
        post_data = {"username": username, "password": password}
        app.post_json("/api/register", post_data)

        response = app.post_json("/api/login", post_data)
        token = response.json["token"]

        headers = {
            "Authorization": f"Bearer {token}",
            "ContentType": "Application/json"
        }
        response = app.get("/api/user/profile", headers=headers)
        data = response.json["data"]
        data["name"] = name
        data["gender"] = gender

        response = app.post_json("/api/user/profile", data, headers=headers)
        assert response.status_code == 202

        response = app.get("/api/user/profile", headers=headers)
        assert response.json["data"] == data


class TestFoodSearch:
    """
    users can record weight
    """

    @given(
        username=st.emails(),
        password=st.text(alphabet=ascii_letters)
    )
    @settings(max_examples=1)
    def test_food_search_exact_match(self, username, password):

        engine = create_engine("sqlite://")
        db = SqlAlchemyBackend(engine)
        db.init()

        Session = sessionmaker(bind=engine, autoflush=True)
        chicken = FoodFact(foodname="chicken", fatg=0.5, proteing=6,
                           carbohydrateg=0, calories=28.5)
        steak = FoodFact(foodname="steak", fatg=2, proteing=6)

        session = Session()
        session.add(chicken)
        session.add(steak)
        session.commit()

        app = webtest.TestApp(create_app(backend=db, secret_key="key"))
        post_data = {"username": username, "password": password}
        app.post_json("/api/register", post_data)
        token = app.post_json("/api/login", post_data).json["token"]

        headers = {"Authorization": f"Bearer {token}"}
        params = {"name": "chicken"}
        response = app.get("/api/food/search", params, headers=headers)

        data = response.json["data"]
        assert data[0]["name"] == chicken.foodname
