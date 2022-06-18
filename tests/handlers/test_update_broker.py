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
        payload = {"name": "Broker Name Updated"}

        event = {
            "headers": {"Authorization": "Bearer 9A093608-BCB2-494C-929D-53EB844453EA"},
            "pathParameters": {"uuid": "a21d70b6-1f04-45ff-96c3-b58ff4f5efc1"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": str(self.broker.user.uid)}
            },
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_when_broker_uuid_in_path_is_missing(self):
        expected = {"error": "Broker not found"}
        payload = {"name": "Broker Name Updated"}

        event = {
            "headers": {"Authorization": "Bearer 9A093608-BCB2-494C-929D-53EB844453EA"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": str(self.broker.user.uid)}
            },
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], expected["error"])

    @db_session
    def test_handle_update_without_name(self):
        payload = {}

        event = {
            "headers": {"Authorization": "Bearer 9A093608-BCB2-494C-929D-53EB844453EA"},
            "pathParameters": {"uuid": str(self.broker.uid)},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": str(self.broker.user.uid)}
            },
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", body)

    @db_session
    def test_handle_succeed_when_broker_has_no_accounts(self):
        payload = {"name": "Broker No Account Updated"}

        event = {
            "headers": {"Authorization": "Bearer 9A093608-BCB2-494C-929D-53EB844453EA"},
            "pathParameters": {"uuid": str(self.broker.uid)},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": str(self.broker.user.uid)}
            },
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])

    @db_session
    def test_handle_succeed_when_broker_has_accounts(self):
        payload = {
            "name": "Broker With Accounts Updated",
        }

        event = {
            "headers": {"Authorization": "Bearer 9A093608-BCB2-494C-929D-53EB844453EA"},
            "pathParameters": {"uuid": "29d49a64-220d-452c-a6d4-9ffc67989534"},
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": str(self.broker_with_accounts.user.uid)}
            },
            "body": json.dumps(payload),
        }

        response = update_broker.handle(event, {})

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])
