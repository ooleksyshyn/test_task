import unittest
import jwt
import datetime
import json

from src.api import app, db
from src.models import User, ActivityLog, Post, Like


class UsersApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        user1 = User(name="Name", surname="Surname", password="123", username="user")
        user2 = User(name="Ім'я", surname="Прізвище", password="123", username="користувач")
        user3 = User(name="Peter", surname="Peterson", password="ppp228", username="pete")
        user4 = User(name="John", surname="Johnson", password="jj114", username="johnny_2")

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)

        db.session.commit()

        self.users_json = [user1.json(), user2.json(), user3.json(), user4.json()]

    def tearDown(self):
        db.session.query(ActivityLog).delete()
        db.session.query(Like).delete()
        db.session.query(Post).delete()
        db.session.query(User).delete()

        db.session.commit()

    def test_get(self):
        r = self.app.get("/api/users")

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, self.users_json)

    def test_post(self):
        name = "Tom"
        surname = "Tompson"
        password = "tommy79"
        username = "tommy_gun"

        data = {
            "name": name,
            "surname": surname,
            "password": password,
            "username": username
        }

        r = self.app.post("/api/users", content_type="application/json", data=json.dumps(data))

        self.assertEqual(r.status_code, 200)

        token = r.json["token"]

        new_user = User.query[-1]

        self.assertEqual(new_user.name, name)
        self.assertEqual(new_user.surname, surname)
        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.password, password)

        created_username = jwt.decode(token, app.config["SECRET_KEY"]).get("username")

        self.assertEqual(username, created_username)

    def test_post_without_data(self):

        r = self.app.post("/api/users")

        self.assertEqual(r.status_code, 404)

    def test_with_existing_username(self):
        username = "pete"

        data = {
            "name": "other_name",
            "surname": "other_surname",
            "password": "other_password",
            "username": username
        }

        r = self.app.post("/api/users", content_type="application/json", data=json.dumps(data))

        self.assertEqual(r.status_code, 404)
        self.assertEqual(
            r.json,
            {'error': 'cant create user with name other_name, surname other_surname, '
                      'username pete, password other_password'}
        )

    def test_post_create_without_name(self):
        # test create without name

        data = {
            "surname": "other_surname",
            "password": "other_password",
            "username": "username228"
        }

        r = self.app.post("/api/users", content_type="application/json", data=json.dumps(data))

        self.assertEqual(r.status_code, 404)
        self.assertEqual(
            r.json,
            {
                'error': 'cant create user with name None, surname other_surname, '
                         'username username228, password other_password'
            }
        )

    def test_post_create_without_surname(self):

        data = {
            "name": "new_name",
            "password": "other_password",
            "username": "username228"
        }

        r = self.app.post("/api/users", content_type="application/json", data=json.dumps(data))

        self.assertEqual(r.status_code, 404)
        self.assertEqual(
            r.json,
            {
                'error': 'cant create user with name new_name, surname None, '
                         'username username228, password other_password'
            }
        )
