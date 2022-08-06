import json
import unittest

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import update_account


class TestUpdateAccount(unittest.TestCase):
    @db_session
    def setUp(self):
        user = User(uid="f93a5e95-e325-4667-b96c-6128ede43ed8", encrypted_password="123456")

        broker = Broker(
            uid="81775d5a-0bbd-4a08-9f91-b627de312d7d",
            name="Test Broker",
            user=user,
        )

        self.account = Account(
            uid="5963c62e-1c35-4d88-b461-6b9de46b4bf9",
            type_account="D",
            currency="USD",
            initial_balance=500.0,
            broker=broker,
            user=user,
        )

        self.another_broker = Broker(
            uid="8b53a64a-9ccb-4db0-849e-dabb67341029",
            name="Another Test Broker",
            user=user,
        )

        another_user = User(uid="f0bf8275-fec6-4f00-9ef3-50db7ec7712b", encrypted_password="123456")

        self.another_account = Account(
            uid="a66ba9cf-b3ee-43a8-85a6-1a00e9e626c9",
            type_account="D",
            currency="USD",
            initial_balance=500.0,
            broker=broker,
            user=another_user,
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    def test_handle_succeed(self):
        payload = {
            "type_account": "R",
            "currency": "BRL",
            "broker_id": "8b53a64a-9ccb-4db0-849e-dabb67341029",
            "initial_balance": 1000.0,
        }

        event = {
            "header": {"Authorization": "Bearer b2d63394-c9f8-4e51-96c4-5746c653938b"},
            "pathParameters": {"uuid": str(self.account.uid)},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "f93a5e95-e325-4667-b96c-6128ede43ed8"}
            },
            "body": json.dumps(payload),
        }

        response = update_account.handle(event, {})

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])

        with db_session:
            updated_account = Account.get(uid=str(self.account.uid))

            self.assertEqual(updated_account.type_account, "R")
            self.assertEqual(updated_account.currency, "BRL")
            self.assertEqual(updated_account.initial_balance, 1000.0)

    def test_handle_invalid_payload(self):
        payload = {
            "type_account": "R",
            "broker_id": "8b53a64a-9ccb-4db0-849e-dabb67341029",
            "initial_balance": 1000.0,
        }

        event = {
            "header": {"Authorization": "Bearer b2d63394-c9f8-4e51-96c4-5746c653938b"},
            "pathParameters": {"uuid": str(self.account.uid)},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "f93a5e95-e325-4667-b96c-6128ede43ed8"}
            },
            "body": json.dumps(payload),
        }

        response = update_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["message"], "'currency' is a required field")

    def test_handle_account_does_not_exist(self):
        payload = {
            "type_account": "R",
            "currency": "BRL",
            "broker_id": "8b53a64a-9ccb-4db0-849e-dabb67341029",
            "initial_balance": 1000.0,
        }

        event = {
            "header": {"Authorization": "Bearer b2d63394-c9f8-4e51-96c4-5746c653938b"},
            "pathParameters": {"uuid": "ae9cad72-8f1d-478a-9949-aea7cc063c0b"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "f93a5e95-e325-4667-b96c-6128ede43ed8"}
            },
            "body": json.dumps(payload),
        }

        response = update_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["message"], "Invalid broker or account")

    def test_handle_account_does_not_belong_to_user(self):
        payload = {
            "type_account": "R",
            "currency": "BRL",
            "broker_id": "8b53a64a-9ccb-4db0-849e-dabb67341029",
            "initial_balance": 1000.0,
        }

        event = {
            "header": {"Authorization": "Bearer b2d63394-c9f8-4e51-96c4-5746c653938b"},
            "pathParameters": {"uuid": str(self.another_account)},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "f93a5e95-e325-4667-b96c-6128ede43ed8"}
            },
            "body": json.dumps(payload),
        }

        response = update_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["message"], "Invalid broker or account")
