import json
import unittest

from pony.orm import db_session

from entities import User, Strategy
from handlers import create_strategy


class TestCreateStrategy(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        User(uid="573f2000-d491-4b17-9088-f817b321c6d8", encrypted_password="123456")

    @classmethod
    @db_session
    def tearDownClass(cls):
        User.select().delete()

    def test_create_strategy_succeed(self):
        payload = {"name": "Strategy test"}

        event = {
            "header": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "573f2000-d491-4b17-9088-f817b321c6d8"}
            },
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(body, dict)
        self.assertEqual(response["statusCode"], 201)
        self.assertIn("uid", body)

        with db_session:
            strategy = Strategy.get(uid=body["uid"])

            self.assertEqual(strategy.name, "Strategy test")
            self.assertEqual(str(strategy.user.uid), "573f2000-d491-4b17-9088-f817b321c6d8")

    def test_create_strategy_failed(self):
        payload = {}
        expected = "'name' is a required field"

        event = {
            "header": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "573f2000-d491-4b17-9088-f817b321c6d8"}
            },
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(body, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected)

    def test_create_strategy_invalid_payload(self):
        payload = {"name": 123}
        expected = "'name' must be of type str"

        event = {
            "header": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "573f2000-d491-4b17-9088-f817b321c6d8"}
            },
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(body, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected)
