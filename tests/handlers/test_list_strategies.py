import json
import unittest

from entities import User, Strategy
from handlers import list_strategies
from pony.orm import db_session


class TestListStrategies(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        user_with_strategies = User(
            uid="7035a52c-4e98-45de-b9cf-5de97d5b5bb5",
            encrypted_password="test123",
            name="User with strategy",
            email="test@mail.com",
            risk=7,
        )

        User(
            uid="9ffd48cb-ce6b-4fe2-a4fb-9073920c7dec",
            encrypted_password="test123",
            name="User without strategy",
            email="test2@mail.com",
            risk=7,
        )

        Strategy(
            uid="2d63b31b-98ce-42d3-a88f-5571ef2dea2d", name="Strategy 1", user=user_with_strategies
        )

        Strategy(
            uid="837614e4-6f2a-4867-b9d1-aa872cc84cd3", name="Strategy 2", user=user_with_strategies
        )

    def setUp(self):
        self.event = {
            "requestContext": {
                "headers": {"Authorizarion": "Bearer api-key"},
                "authorizer": {"user_uuid": "7035a52c-4e98-45de-b9cf-5de97d5b5bb5", "sub": "auth0"},
            }
        }

    @classmethod
    @db_session
    def tearDownClass(cls):
        Strategy.select().delete()
        User.select().delete()

    def test_handle_succeed(self):
        expected = {
            "strategies": [
                {"uid": "2d63b31b-98ce-42d3-a88f-5571ef2dea2d", "name": "Strategy 1"},
                {"uid": "837614e4-6f2a-4867-b9d1-aa872cc84cd3", "name": "Strategy 2"},
            ]
        }

        response = list_strategies.handle(self.event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertDictEqual(expected, body)

    def test_handle_succeed_user_with_no_strategy(self):
        self.event["requestContext"]["authorizer"][
            "user_uuid"
        ] = "9ffd48cb-ce6b-4fe2-a4fb-9073920c7dec"

        expected = {"strategies": []}

        response = list_strategies.handle(self.event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertDictEqual(expected, body)
