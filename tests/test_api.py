import unittest


from src.api import app, db


class UsersApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get(self):
        r = self.app.get("api/users")

        # print(r.json())
        self.assertEqual(r.status_code, 200)
