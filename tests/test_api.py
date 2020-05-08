import unittest
import requests


class UsersApiTest(unittest.TestCase):
    def test_get(self):
        r = requests.get("http://localhost:5000/api/users")

        # print(r.json())
        self.assertEqual(r.status_code, 200)
