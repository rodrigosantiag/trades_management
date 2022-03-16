import json
import unittest
from operator import itemgetter

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import list_brokers


class TestListBrokers(unittest.TestCase):
    @db_session
    def setUp(self):
        self.uid_user_without_broker = "f3f54c24-7835-4087-be1e-2896bfcf9405"
        self.uid_user_one_broker = "3a72189d-0c92-4413-8900-29295e2a3337"
        self.uid_user_two_brokers = "e4da67b2-336e-4e1d-97dd-97a7b645f25e"

        self.user_without_broker = User(
            uid=self.uid_user_without_broker,
            encrypted_password="test123",
            name="User without broker",
            email="nobroker@mail.com",
            risk=7,
        )

        self.user_with_one_broker = User(
            uid=self.uid_user_one_broker,
            encrypted_password="test123",
            name="User with one broker",
            email="onebroker@mail.com",
            risk=1,
        )

        self.user_with_two_brokers = User(
            uid=self.uid_user_two_brokers,
            encrypted_password="test123",
            name="User with two brokers",
            email="twobrokers@mail.com",
            risk=2,
        )

        Broker(
            uid="0a3a52c8-f8d5-4b7c-8dcd-e946b9728052",
            name="Broker 1",
            user=User.get(uid=self.uid_user_one_broker),
        )

        Broker(
            uid="1c9d4709-1feb-405a-bb36-7c70d020aebf",
            name="Broker 2",
            user=User.get(uid=self.uid_user_two_brokers),
        )

        Broker(
            uid="efd96fcf-0c8c-4016-a0e9-c3a7292e71f3",
            name="Broker 3",
            user=User.get(uid=self.uid_user_two_brokers),
        )

        Account(
            uid="8ab16f88-0e77-4130-a47c-5cd18f59a814",
            type_account="D",
            currency="USD",
            initial_balance=100,
            current_balance=100,
            broker=Broker.get_by_uid("1c9d4709-1feb-405a-bb36-7c70d020aebf"),
            user=User.get(uid=self.uid_user_two_brokers),
        )

        Account(
            uid="7aafd19e-3f1d-40a7-87ff-ebc4eb381d48",
            type_account="R",
            currency="USD",
            initial_balance=1000,
            current_balance=100,
            broker=Broker.get_by_uid("efd96fcf-0c8c-4016-a0e9-c3a7292e71f3"),
            user=User.get(uid=self.uid_user_two_brokers),
        )

        Account(
            uid="a733afe5-8b00-43d4-98db-c482b43cc475",
            type_account="D",
            currency="BRL",
            initial_balance=100000,
            current_balance=10000,
            broker=Broker.get_by_uid("efd96fcf-0c8c-4016-a0e9-c3a7292e71f3"),
            user=User.get(uid=self.uid_user_two_brokers),
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_handle_missing_user_id(self):
        event = {"headers": {"x-api-key": "api-key"}, "queryStringParameters": {}}

        result = list_brokers.handle(event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 400)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["error"], "Missing user ID")

    @db_session
    def test_handle_user_with_no_broker(self):
        query_parameters = {"user_id": self.user_without_broker.id}

        event = {"headers": {"x-api-key": "api-key"}, "queryStringParameters": query_parameters}

        result = list_brokers.handle(event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body["brokers"]), 0)

    @db_session
    def test_handle_user_with_one_broker(self):
        expected = {
            "brokers": [
                {"uid": "0a3a52c8-f8d5-4b7c-8dcd-e946b9728052", "name": "Broker 1", "accounts": []}
            ]
        }

        query_parameters = {"user_id": self.user_with_one_broker.id}

        event = {"headers": {"x-api-key": "api-key"}, "queryStringParameters": query_parameters}

        result = list_brokers.handle(event, {})
        body = json.loads(result["body"])

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body["brokers"][0]["uid"], expected["brokers"][0]["uid"])
        self.assertEqual(body["brokers"][0]["name"], expected["brokers"][0]["name"])
        self.assertEqual(len(body["brokers"][0]["accounts"]), 0)

    @db_session
    def test_handle_user_with_two_brokers(self):
        expected = {
            "brokers": [
                {
                    "uid": "1c9d4709-1feb-405a-bb36-7c70d020aebf",
                    "name": "Broker 2",
                    "accounts": [
                        {
                            "uid": "8ab16f88-0e77-4130-a47c-5cd18f59a814",
                            "type_account": "D",
                            "currency": "USD",
                            "initial_balance": 100.0,
                            "current_balance": 100.0,
                        },
                    ],
                },
                {
                    "uid": "efd96fcf-0c8c-4016-a0e9-c3a7292e71f3",
                    "name": "Broker 3",
                    "accounts": [
                        {
                            "uid": "7aafd19e-3f1d-40a7-87ff-ebc4eb381d48",
                            "type_account": "R",
                            "currency": "USD",
                            "initial_balance": 1000.0,
                            "current_balance": 100.0,
                        },
                        {
                            "uid": "a733afe5-8b00-43d4-98db-c482b43cc475",
                            "type_account": "D",
                            "currency": "BRL",
                            "initial_balance": 100000.0,
                            "current_balance": 10000.0,
                        },
                    ],
                },
            ],
        }

        query_parameters = {"user_id": self.user_with_two_brokers.id}

        event = {"headers": {"x-api-key": "api-key"}, "queryStringParameters": query_parameters}

        result = list_brokers.handle(event, {})
        body = json.loads(result["body"])

        sorted_expected = sorted(expected["brokers"], key=itemgetter("uid"))
        sorted_result = sorted(body["brokers"], key=itemgetter("uid"))

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(sorted_expected[0]["uid"], sorted_result[0]["uid"])
        self.assertEqual(sorted_expected[0]["name"], sorted_result[0]["name"])
        self.assertListEqual(
            sorted(sorted_expected[0]["accounts"], key=itemgetter("uid")),
            sorted(sorted_result[0]["accounts"], key=itemgetter("uid")),
        )

        self.assertEqual(sorted_expected[1]["uid"], sorted_result[1]["uid"])
        self.assertEqual(sorted_expected[1]["name"], sorted_result[1]["name"])
        self.assertListEqual(
            sorted(sorted_expected[1]["accounts"], key=itemgetter("uid")),
            sorted(sorted_result[1]["accounts"], key=itemgetter("uid")),
        )

        self.assertEqual(len(sorted_result[0]["accounts"]), 1)
        self.assertEqual(len(sorted_result[1]["accounts"]), 2)
