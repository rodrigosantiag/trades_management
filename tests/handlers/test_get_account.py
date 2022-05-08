import json
import unittest

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import get_account


@unittest.skip
class TestGetAccount(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        user = User(
            uid="a7d275ee-af60-4fae-a69e-2a4f12d57f2d",
            encrypted_password="1234456",
        )

        broker = Broker(
            uid="77c60c8c-46f2-4f67-8956-762f4bfd0210",
            name="Test Broker",
            user=user,
        )

        Account(
            uid="26e369c9-b2db-44cd-9c1c-0c679a92cc40",
            type_account="R",
            currency="USD",
            initial_balance=100.0,
            current_balance=500.0,
            broker=broker,
            user=user,
        )

    def setUp(self):
        self.event = {
            "headers": {"Authorization": "Bearer foobar"},
            "requestContext": {
                "authorizer": {
                    "sub": "auth0",
                    "user_uuid": "a7d275ee-af60-4fae-a69e-2a4f12d57f2d",
                }
            },
            "pathParameters": {"uuid": "26e369c9-b2db-44cd-9c1c-0c679a92cc40"},
        }

    @classmethod
    @db_session
    def tearDownClass(cls):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    @db_session
    def test_get_account_succeed(self):
        result = get_account.handle(self.event, {})
        body = json.loads(result["body"])

        # expected = {
        #     "broker_uuid": "77c60c8c-46f2-4f67-8956-762f4bfd0210",
        #     "type_account": "R",
        #     # TODO: continue tests
        # }

        self.assertEqual(result["statusCode"], 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body)
