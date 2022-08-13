import json
import unittest

from pony.orm import db_session

from entities import User, Strategy
from handlers import update_strategy


class TestUpdateStrategy(unittest.TestCase):
    @db_session
    def setUp(self):
        self.user = User(
            uid="d3abce38-97f5-4211-b5e2-520f771f5330",
            encrypted_password="123445",
        )

        Strategy(
            uid="e28813e7-5e9c-4e2d-98bf-e5fed66cc20c",
            name="Test strategy",
            user=self.user,
        )

        self.event = {
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": "d3abce38-97f5-4211-b5e2-520f771f5330",
                }
            },
            "pathParameters": {"uuid": "e28813e7-5e9c-4e2d-98bf-e5fed66cc20c"},
            "headers": {"Authorization": "jwt-token"},
            "body": json.dumps({"name": "Strategy name updated"}),
        }

    @db_session
    def tearDown(self):
        Strategy.select().delete()
        User.select().delete()

    def test_handle_succeed(self):
        response = update_strategy.handle(self.event, {})

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])

        with db_session:
            strategy = Strategy.get(uid="e28813e7-5e9c-4e2d-98bf-e5fed66cc20c")

            self.assertEqual(strategy.name, "Strategy name updated")

    def test_handle_not_found_strategy(self):
        expected = {"message": "Strategy not found"}
        self.event["pathParameters"]["uuid"] = "f3aa5f63-37ba-4959-a2c4-a71f7b680c59"

        response = update_strategy.handle(self.event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertDictEqual(body, expected)

    def test_handle_missing_path_parameters(self):
        expected = {"message": "Strategy not found"}
        self.event["pathParameters"]["uuid"] = None

        response = update_strategy.handle(self.event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertDictEqual(body, expected)

    def test_handle_invalid_payload(self):
        subtest_params = (
            ({"name": 1}, "'name' must be of type str"),
            ({"foo": "bar"}, "'name' is a required field"),
        )

        for params in subtest_params:
            request_body, message = params

            with self.subTest(request_body=request_body, message=message):
                self.event["body"] = json.dumps(request_body)

                response = update_strategy.handle(self.event, {})
                body = json.loads(response["body"])

                self.assertEqual(response["statusCode"], 400)
                self.assertEqual(body["message"], message)
