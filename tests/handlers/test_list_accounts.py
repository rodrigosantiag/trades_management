import json
import unittest

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import list_accounts


@unittest.skip
class TestListAccounts(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        User(
            uid="f1cbf074-09fc-4cac-92a2-dac5ba65efdc",
            encrypted_password="123456",
        )

        user = User(
            uid="2717bb51-984b-47a2-9824-e419666e3683",
            encrypted_password="123456",
        )

        broker1 = Broker(
            uid="f124fd21-f248-4e52-897b-4a55e35e8272",
            name="Broker 1",
            user=user,
        )

        broker2 = Broker(
            uid="9c4990d4-a582-438c-b3e5-41235941422c",
            name="Broker 2",
            user=user,
        )

        Account(
            uid="145c3913-7750-44b8-8e42-f8ed3f5e5e82",
            type_account="R",
            currency="USD",
            initial_balance=100.0,
            current_balance=150.0,
            broker=broker1,
            user=user,
        )

        Account(
            uid="50ce2909-ed98-45a0-8c6a-f1404549a0cc",
            type_account="D",
            currency="USD",
            initial_balance=10000.0,
            current_balance=10000.0,
            broker=broker1,
            user=user,
        )

        Account(
            uid="0163f6d3-f07e-42ac-bc36-17e63c704279",
            type_account="R",
            currency="BRL",
            initial_balance=500.0,
            current_balance=799.98,
            broker=broker2,
            user=user,
        )

        Account(
            uid="982df24f-b7fa-4402-af5d-962e48fb7195",
            type_account="D",
            currency="BRL",
            initial_balance=50000.0,
            current_balance=150567.0,
            broker=broker2,
            user=user,
        )

    def setUp(self):
        self.event = {
            "headers": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": "2717bb51-984b-47a2-9824-e419666e3683",
                }
            },
        }

        self.expected = {
            "accounts": [
                {
                    "uid": "145c3913-7750-44b8-8e42-f8ed3f5e5e82",
                    "type_account": "R",
                    "currency": "USD",
                    "initial_balance": 100.0,
                    "current_balance": 150.0,
                    "broker": {"name": "Broker 1"},
                },
                {
                    "uid": "50ce2909-ed98-45a0-8c6a-f1404549a0cc",
                    "type_account": "D",
                    "currency": "USD",
                    "initial_balance": 10000.0,
                    "current_balance": 10000.0,
                    "broker": {"name": "Broker 1"},
                },
                {
                    "uid": "0163f6d3-f07e-42ac-bc36-17e63c704279",
                    "type_account": "R",
                    "currency": "BRL",
                    "initial_balance": 500.0,
                    "current_balance": 799.98,
                    "broker": {"name": "Broker 2"},
                },
                {
                    "uid": "982df24f-b7fa-4402-af5d-962e48fb7195",
                    "type_account": "D",
                    "currency": "BRL",
                    "initial_balance": 50000.0,
                    "current_balance": 150567.0,
                    "broker": {"name": "Broker 2"},
                },
            ]
        }

    @classmethod
    @db_session
    def tearDownClass(cls):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    def test_handle_list_no_accounts(self):
        self.event["requestContext"]["authorizer"][
            "user_uuid"
        ] = "f1cbf074-09fc-4cac-92a2-dac5ba65efdc"

        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["accounts"]), 0)

    def test_handle_list_all_accounts(self):
        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["accounts"]), 4)
        self.assertDictEqual(body["accounts"][0], self.expected["accounts"][0])
        self.assertDictEqual(body["accounts"][1], self.expected["accounts"][1])
        self.assertDictEqual(body["accounts"][2], self.expected["accounts"][2])
        self.assertDictEqual(body["accounts"][3], self.expected["accounts"][3])

    def test_handle_list_filtered_accounts_by_broker(self):
        self.event["queryParameters"] = {
            "broker_uid": "f124fd21-f248-4e52-897b-4a55e35e8272",
        }

        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["accounts"]), 2)
        self.assertDictEqual(body["accounts"][0], self.expected["accounts"][0])
        self.assertDictEqual(body["accounts"][1], self.expected["accounts"][1])

    def test_handle_list_filtered_accounts_by_type_account(self):
        self.event["queryParameters"] = {
            "type_account": "D",
        }

        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["accounts"]), 2)
        self.assertDictEqual(body["accounts"][0], self.expected["accounts"][1])
        self.assertDictEqual(body["accounts"][1], self.expected["accounts"][3])

    def test_handle_list_filtered_accounts_by_broker_and_type_account(self):
        self.event["queryParameters"] = {
            "broker_uid": "9c4990d4-a582-438c-b3e5-41235941422c",
            "type_account": "R",
        }

        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["accounts"]), 1)
        self.assertDictEqual(body["accounts"][0], self.expected["accounts"][2])

    def test_handle_list_filtered_accounts_by_invalid_parameter(self):
        self.event["queryParameters"] = {
            "broker_name": "Broker 1",
        }

        result = list_accounts.handle(self.event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["error"], "Invalid query parameter")
