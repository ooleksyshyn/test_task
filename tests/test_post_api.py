import unittest
import jwt
import json


from src.api import app, db
from src.models import User, Post, Like, clear_db


class PostsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        user1 = User(name="name", surname="surname", password="password", username="user1")
        user2 = User(name="name2", surname="surname2", password="password2", username="user2")

        db.session.add(user1)
        db.session.add(user2)

        post1 = Post(author_id=user1.id, text="Directed by R. B. Weirde")
        post2 = Post(author_id=user1.id, text="My second post: I've just turned 18! Congrats to me!!!")
        post3 = Post(author_id=user2.id, text="I think I`m very good at doing nothing")
        post4 = Post(author_id=user2.id, text="Йой, най буде")

        db.session.add(post1)
        db.session.add(post2)
        db.session.add(post3)
        db.session.add(post4)

        db.session.commit()

        self.posts_json = [post1.json(), post2.json(), post3.json(), post4.json()]
        self.users_json = [user1.json(), user2.json()]

    def tearDown(self):
        clear_db()

    def test_get(self):
        r = self.app.get("/api/posts")

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, self.posts_json)

    def test_post(self):
        for user in self.users_json:
            username, password = user["username"], user["password"]

            login_data = {"username": username, "password": password}

            token = self.app.get(
                "/api/login",
                content_type="application/json",
                data=json.dumps(login_data)
            ).json.get("token")

            text = f"{username} wants to test if I can create a new post. Навіть якщо він написаний двома мовами"
            post_data = {"text": text}

            r = self.app.post(
                "/api/posts",
                content_type="application/json",
                data=json.dumps(post_data),
                headers={"X-Api-Key": token}
            )

            self.assertEqual(r.status_code, 201)
            self.assertEqual(r.json.get("text"), text)

            # check if post was created for right user
            self.assertEqual(r.json.get("author_id"), user["id"])

            post_in_database = self.app.get("/api/posts").json

            # check if last post is our new post
            self.assertEqual(post_in_database[-1]["text"], text)
            self.assertEqual(post_in_database[-1]["author_id"], user["id"])

    def test_post_unauthorized(self):
        token = "someinvalidtoken"

        text = f"I want to test if I can create a new post"
        post_data = {"text": text}

        r = self.app.post(
            "/api/posts",
            content_type="application/json",
            data=json.dumps(post_data),
            headers={"X-Api-Key": token}
        )

        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json, {"token required": "wrong token"})

    def test_post_without_data(self):
        username, password = self.users_json[1]["username"], self.users_json[1]["password"]

        login_data = {"username": username, "password": password}

        token = self.app.get(
            "/api/login",
            content_type="application/json",
            data=json.dumps(login_data)
        ).json.get("token")

        text = f"{username} wants to test if I can create a new post"
        post_data = {"text": text}

        r = self.app.post(
            "/api/posts",
            content_type="application/json",
            headers={"X-Api-Key": token}
        )

        self.assertEqual(r.status_code, 400)

        r = self.app.post(
            "/api/posts",
            headers={"X-Api-Key": token}
        )

        self.assertEqual(r.status_code, 401)

