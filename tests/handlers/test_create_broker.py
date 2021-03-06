import json
import unittest
from datetime import datetime
from uuid import uuid4

from pony.orm import db_session

from entities import Broker, User
from handlers import create_broker


class TestCreateBroker(unittest.TestCase):
    @db_session
    def setUp(self):
        self.user = User(
            uid=uuid4(),
            encrypted_password="test123",
            confirmed_at=datetime(2021, 1, 1, 0, 0, 0),
            name="John Doe",
            email="foo@bar.com",
            risk=7,
            created_at=datetime(1970, 1, 1, 0, 0, 0),
            updated_at=datetime(1970, 1, 1, 0, 0, 0),
        )

        self.data = {"name": "Broker Post Create"}

    @db_session
    def tearDown(self):
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_handle_succeed(self):
        event = {
            "headers": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": self.user.uid,
                }
            },
            "body": json.dumps(self.data),
        }

        response = create_broker.handle(event, {})

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 201)

        body = json.loads(response["body"])

        broker = Broker.get(uid=body["uid"])

        self.assertIsInstance(broker, Broker)
        self.assertIsNotNone(broker.uid)
        self.assertEqual(broker.name, "Broker Post Create")
        self.assertIsInstance(broker.user, User)

    @db_session
    def test_handle_failed(self):
        del self.data["name"]
        expected = "'name' is a required field"

        event = {
            "headers": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": self.user.uid,
                }
            },
            "body": json.dumps(self.data),
        }

        response = create_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], expected)

    @db_session
    def test_handle_invalid_payload(self):
        self.data["name"] = 4356.9

        event = {
            "headers": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": self.user.uid,
                }
            },
            "body": json.dumps(self.data),
        }

        response = create_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertIsInstance(response, dict)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["message"], "'name' must be of type str")
