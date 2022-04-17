import json
import unittest

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import create_account


class TestCreateAccount(unittest.TestCase):
    @db_session
    def setUp(self):
        self.user = User(uid="24fc13a5-e696-4434-b4f2-4f44799cbfa0", encrypted_password="123456")

        self.another_user = User(
            uid="d059156c-ecb4-4786-9bac-b97ee3958126", encrypted_password="123456"
        )

        self.broker = Broker(
            uid="901d54a0-c677-494e-8164-de410736e18a",
            name="Test Broker",
            user=User.get(uid="24fc13a5-e696-4434-b4f2-4f44799cbfa0"),
        )

        self.another_broker = Broker(
            uid="f423b9b8-01c3-46f3-b7d4-4dbd1846ccd4",
            name="Test Broker Another User",
            user=User.get(uid="d059156c-ecb4-4786-9bac-b97ee3958126"),
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_handle_succeed(self):
        payload = {
            "type_account": "R",
            "currency": "USD",
            "initial_balance": 1000.0,
            "broker_uid": str(self.broker.uid),
        }

        event = {
            "headers": {"Authorization": "Bearer token-jwt"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": str(self.user.uid)}},
            "body": json.dumps(payload),
        }

        response = create_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 201)
        self.assertIsInstance(body, dict)
        self.assertIn("uid", body)

        account = Account.get(uid=body["uid"])

        self.assertIsInstance(account, Account)
        self.assertIsNotNone(account.uid)
        self.assertEqual(account.type_account, "R")
        self.assertEqual(account.currency, "USD")
        self.assertEqual(account.initial_balance, 1000.0)
        self.assertEqual(account.current_balance, 1000.0)
        self.assertIsInstance(account.broker, Broker)
        self.assertEqual(account.broker.id, self.broker.id)
        self.assertIsInstance(account.user, User)
        self.assertEqual(account.user.id, self.user.id)

    @db_session
    def test_handle_invalid_payload(self):
        payload = {
            "currency": "USD",
            "initial_balance": 1000.0,
            "current_balance": 1000.0,
            "broker_uid": str(self.broker.uid),
        }

        event = {
            "headers": {"Authorization": "Bearer token-jwt"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": str(self.user.uid)}},
            "body": json.dumps(payload),
        }

        expected = {"error": "'type_account' must be of type str"}

        response = create_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_create_account_into_another_user_broker(self):
        payload = {
            "currency": "BRL",
            "initial_balance": 100.0,
            "current_balance": 100.0,
            "broker_uid": str(self.another_broker.uid),
        }

        event = {
            "headers": {"Authorization": "Bearer token-jwt"},
            "requestContext": {"authorizer": {"sub": "auth0", "user_uuid": str(self.user.uid)}},
            "body": json.dumps(payload),
        }

        expected = {"error": "Invalid broker"}

        response = create_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["error"], expected["error"])
