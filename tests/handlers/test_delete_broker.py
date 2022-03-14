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

        self.broker = Broker(
            uid="85808508-2259-4704-a9d5-619533ad518a",
            name="Test broker",
            user=User.get(uid="ee46e9b2-d01a-4b36-9a30-d94cbcb18894"),
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
    def test_handle_broker_does_not_exist(self):
        expected = {"error": "Broker not found"}

        payload = {"uid": "84d5d8e4-aaee-4dae-84a7-4542f43fceba", "user_id": self.broker.user.id}

        event = {
            "headers": {"x-api-key": "b5dd5226-2f8e-4724-b67e-2369762c6a73"},
            "body": json.dumps(payload),
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_broker_with_invalid_payload(self):
        expected = {"error": "Broker not found"}

        payload = {
            "uid": "85808508-2259-4704-a9d5-619533ad518a",
        }

        event = {
            "headers": {"x-api-key": "b5dd5226-2f8e-4724-b67e-2369762c6a73"},
            "body": json.dumps(payload),
        }

        response = delete_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_succeed(self):
        payload = {"uid": "85808508-2259-4704-a9d5-619533ad518a", "user_id": self.broker.user.id}

        event = {
            "headers": {"x-api-key": "b5dd5226-2f8e-4724-b67e-2369762c6a73"},
            "body": json.dumps(payload),
        }

        response = delete_broker.handle(event, {})

        broker = Broker.get_by_uid("85808508-2259-4704-a9d5-619533ad518a")

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])
        self.assertIsNone(broker)
