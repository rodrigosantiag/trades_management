import json
import unittest

from pony.orm import db_session

from entities import User, Strategy
from handlers import create_strategy


class TestCreateStrategy(unittest.TestCase):
    @db_session
    def setUp(self):
        self.user = User(uid="c24a69bc-82e3-4fa3-8aae-f2db665edd53", encrypted_password="123456")

    @db_session
    def tearDown(self):
        Strategy.select().delete()
        User.select().delete()

    def test_handle_succeed(self):
        payload = {"name": "Test Strategy"}

        event = {
            "headers": {"Authorization": "Bearer foo-bar-token"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": self.user.uid}},
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 201)
        self.assertIn("uid", body)

        with db_session:
            strategy = Strategy.get(uid=body["uid"])

            self.assertIsInstance(strategy.user, User)
            self.assertIsNotNone(strategy.uid)
            self.assertEqual(strategy.name, "Test Strategy")

    def test_handle_missing_field(self):
        payload = {"foo": "bar"}

        event = {
            "headers": {"Authorization": "foo-bar-token"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": self.user.uid,
                }
            },
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "'name' is a required field")

    def test_handle_invalid_payload(self):
        payload = {"name": True}

        event = {
            "headers": {"Authorization": "foo-bar-token"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": self.user.uid,
                }
            },
            "body": json.dumps(payload),
        }

        response = create_strategy.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "'name' must be of type str")
