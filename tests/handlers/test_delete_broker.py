import json
import unittest
from datetime import datetime

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import delete_broker


class TestDeleteBroker(unittest.TestCase):
    @db_session
    def setUp(self):
        User(
            uid="ee46e9b2-d01a-4b36-9a30-d94cbcb18894",
            encrypted_password="123456",
            name="Test User",
            email=f"mail{datetime.utcnow()}@mail.com",
            risk=7,
        )

        User(
            uid="e308981d-8918-4d7f-a19e-f03d82dc9663",
            encrypted_password="123456",
            name="Test User 2",
            email=f"mail2{datetime.utcnow()}@mail.com",
            risk=7,
        )

        self.broker = Broker(
            uid="85808508-2259-4704-a9d5-619533ad518a",
            name="Test broker",
            user=User.get(uid="ee46e9b2-d01a-4b36-9a30-d94cbcb18894"),
        )

        Broker(
            uid="e56901f7-2d25-4f2a-994b-706d248f8989",
            name="Test broker 2",
            user=User.get(uid="e308981d-8918-4d7f-a19e-f03d82dc9663"),
        )

        Account(
            uid="859b3e77-be9f-49a5-b70c-ad87160e83f7",
            type_account="D",
            currency="USD",
            initial_balance=10000.0,
            current_balance=10000.0,
            broker=Broker.get(uid="85808508-2259-4704-a9d5-619533ad518a"),
            user=User.get(uid="ee46e9b2-d01a-4b36-9a30-d94cbcb18894"),
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_handle_unauthorized(self):
        expected = {"message": "Unauthorized"}

        event = {
            "headers": {"Authorization": "Bearer xpto"},
            "pathParameters": {"uuid": "84d5d8e4-aaee-4dae-84a7-4542f43fceba"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "b5dd5226-2f8e-4724-b67e-2369762c6a73"}
            },
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 401)
        self.assertEqual(body["message"], expected["message"])

    @db_session
    def test_handle_missing_broker_uuid(self):
        expected = {"message": "Invalid broker"}

        event = {
            "headers": {"Authorization": "Bearer xpto"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": self.broker.user.uid}},
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected["message"])

    @db_session
    def test_handle_badly_formed_path_parameters(self):
        expected = {"message": "Invalid broker"}

        event = {
            "headers": {"Authorization": "Bearer xpto"},
            "pathParameters": {"uuid": "aaaa"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": self.broker.user.uid}},
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected["message"])

    @db_session
    def test_handle_broker_does_not_belong_to_user(self):
        expected = {"message": "Invalid broker"}

        event = {
            "headers": {"Authorization": "Bearer xpto"},
            "pathParameters": {"uuid": "e308981d-8918-4d7f-a19e-f03d82dc9663"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": self.broker.user.uid}},
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected["message"])

    @db_session
    def test_handle_succeed(self):
        event = {
            "headers": {"Authorization": "Bearer xpto"},
            "pathParameters": {"uuid": "85808508-2259-4704-a9d5-619533ad518a"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": self.broker.user.uid}},
        }

        response = delete_broker.handle(event, {})

        broker = Broker.get_by_uid("85808508-2259-4704-a9d5-619533ad518a")

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])
        self.assertIsNone(broker)
