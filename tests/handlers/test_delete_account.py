import json
import unittest

from pony.orm import db_session

from entities import User, Broker, Account
from handlers import delete_account


class TestDeleteAccount(unittest.TestCase):
    @db_session
    def setUp(self):
        user = User(uid="e78ed068-f364-477d-bb98-8a981355c0a9", encrypted_password="1233455")
        broker = Broker(uid="94a4756d-eb7b-44cb-8558-857bb9aa1e9c", name="Test Broker", user=user)

        Account(
            uid="f280b3c0-fabf-4f01-b194-7846cb6c9a26",
            type_account="D",
            currency="USD",
            initial_balance=500,
            broker=broker,
            user=user,
        )

    @db_session
    def tearDown(self):
        Account.select().delete()
        Broker.select().delete()
        User.select().delete()

    def test_handle_succeed(self):
        event = {
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "e78ed068-f364-477d-bb98-8a981355c0a9"}
            },
            "pathParameters": {"uuid": "f280b3c0-fabf-4f01-b194-7846cb6c9a26"},
            "headers": {"Authorization": "Bearer foo-bar"},
        }

        response = delete_account.handle(event, {})

        self.assertEqual(response["statusCode"], 204)
        self.assertIsNone(response["body"])

        with db_session:
            account = Account.get(uid="f280b3c0-fabf-4f01-b194-7846cb6c9a26")

            self.assertIsNone(account)

    def test_handle_account_does_not_exist(self):
        event = {
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "e78ed068-f364-477d-bb98-8a981355c0a9"}
            },
            "pathParameters": {"uuid": "d5acb982-a8b6-460c-be6c-78bce118b63a"},
            "headers": {"Authorization": "Bearer foo-bar"},
        }

        response = delete_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertDictEqual(body, {"message": "Invalid account"})

    def test_handle_account_with_invalid_path(self):
        event = {
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "e78ed068-f364-477d-bb98-8a981355c0a9"}
            },
            "pathParameters": {"uuid": "1"},
            "headers": {"Authorization": "Bearer foo-bar"},
        }

        response = delete_account.handle(event, {})
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertDictEqual(body, {"message": "Invalid account"})
