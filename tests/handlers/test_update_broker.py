import json
import unittest

from pony.orm.core import db_session

from entities import Broker, User, Account
from fixtures import create_sample_broker
from handlers import update_broker


class TestUpdateBroker(unittest.TestCase):
    @db_session
    def setUp(self):
        self.broker = create_sample_broker()

        User(
            uid="d69399ed-1b2b-4873-a1d2-5165d373d02d",
            encrypted_password="test123",
        )

        self.broker_with_accounts = Broker(
            uid="29d49a64-220d-452c-a6d4-9ffc67989534",
            name="Broker With Accounts",
            user=User.get(uid="d69399ed-1b2b-4873-a1d2-5165d373d02d"),
        )

        self.account1 = Account(
            uid="6de4eb98-383b-46a0-a673-bba34aad2c69",
            type_account="D",
            currency="USD",
            initial_balance=10000.0,
            current_balance=10000.0,
            broker=Broker.get(uid="29d49a64-220d-452c-a6d4-9ffc67989534"),
            user=User.get(uid="d69399ed-1b2b-4873-a1d2-5165d373d02d"),
        )

        self.account2 = Account(
            uid="a003ec51-995c-4852-a43d-133f60f41c46",
            type_account="R",
            currency="BRL",
            initial_balance=1000.0,
            current_balance=2000.0,
            broker=Broker.get(uid="29d49a64-220d-452c-a6d4-9ffc67989534"),
            user=User.get(uid="d69399ed-1b2b-4873-a1d2-5165d373d02d"),
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_handle_when_broker_does_not_exist_for_user(self):
        expected = {"error": "Broker not found"}
        payload = {
            "uid": "a21d70b6-1f04-45ff-96c3-b58ff4f5efc1",
            "name": "Broker Name Updated",
            "user_id": self.broker.user.id,
        }

        event = {
            "headers": {"x-api-key": "9A093608-BCB2-494C-929D-53EB844453EA"},
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_update_without_name(self):
        payload = {"uid": str(self.broker.uid), "user_id": self.broker.user.id}

        event = {
            "headers": {"x-api-key": "9A093608-BCB2-494C-929D-53EB844453EA"},
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", body)

    @db_session
    def test_handle_when_clause_is_incomplete(self):
        expected = {"error": "Broker not found"}
        payload = {
            "uid": "a21d70b6-1f04-45ff-96c3-b58ff4f5efc1",
            "name": "Broker Name Updated",
        }

        event = {
            "headers": {"x-api-key": "9A093608-BCB2-494C-929D-53EB844453EA"},
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_succeed_when_broker_has_no_accounts(self):
        expected = {
            "uid": str(self.broker.uid),
            "name": "Broker No Account Updated",
            "accounts": [],
        }

        payload = {
            "uid": str(self.broker.uid),
            "name": "Broker No Account Updated",
            "user_id": self.broker.user.id,
        }

        event = {
            "headers": {"x-api-key": "9A093608-BCB2-494C-929D-53EB844453EA"},
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertIsInstance(body, dict)

        for key, value in expected.items():
            self.assertEqual(body[key], value)

    @db_session
    def test_handle_succeed_when_broker_has_accounts(self):
        expected = {
            "uid": "29d49a64-220d-452c-a6d4-9ffc67989534",
            "name": "Broker With Accounts Updated",
            "accounts": [
                {
                    "uid": "6de4eb98-383b-46a0-a673-bba34aad2c69",
                    "type_account": "D",
                    "currency": "USD",
                    "initial_balance": 10000.0,
                    "current_balance": 10000.0,
                },
                {
                    "uid": "a003ec51-995c-4852-a43d-133f60f41c46",
                    "type_account": "R",
                    "currency": "BRL",
                    "initial_balance": 1000.0,
                    "current_balance": 2000.0,
                },
            ],
        }

        payload = {
            "uid": "29d49a64-220d-452c-a6d4-9ffc67989534",
            "name": "Broker With Accounts Updated",
            "user_id": self.broker_with_accounts.user.id,
        }

        event = {
            "headers": {"x-api-key": "9A093608-BCB2-494C-929D-53EB844453EA"},
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertIsInstance(body, dict)

        for key, value in expected.items():
            self.assertEqual(body[key], value)
