import json
import unittest
from datetime import datetime

from pony.orm import db_session
from serpens import api

import helpers
from entities import User


class TestAuthorized(unittest.TestCase):
    @classmethod
    @db_session
    def setUpClass(cls):
        User(
            uid="802bee76-78f6-4113-a8a5-8562df5a2901",
            encrypted_password="123456",
            name="John Doe",
            email="john@doe.com",
            risk=7,
            created_at=datetime(1970, 1, 1, 0, 0, 0),
            updated_at=datetime(1970, 1, 1, 0, 0, 0),
        )

    @classmethod
    @db_session
    def tearDownClass(cls):
        User.select().delete()

    def test_authorize_with_user_uuid(self):
        with db_session:
            event = {
                "requestContext": {
                    "authorizer": {
                        "sub": "auth0",
                        "user_uuid": "802bee76-78f6-4113-a8a5-8562df5a2901",
                    }
                }
            }

            expected = {
                "headers": {"Access-Control-Allow-Origin": "*"},
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "user_uuid": "802bee76-78f6-4113-a8a5-8562df5a2901",
                    }
                ),
            }

        @helpers.authorized
        def handler(request: api.Request):
            return json.dumps(
                {"user_uuid": request.authorizer.user_uuid},
            )

        response = handler(event, {})
        self.assertDictEqual(response, expected)

    def test_unauthorized_user(self):
        event = {
            "requestContext": {
                "authorizer": {"sub": "auth0", "user_uuid": "f81eede8-b785-4e88-933b-31666434170e"}
            }
        }

        expected = {
            "headers": {"Access-Control-Allow-Origin": "*"},
            "statusCode": 401,
            "body": json.dumps(
                {
                    "message": "Unauthorized",
                }
            ),
        }

        @helpers.authorized
        def handler(request):
            return {"message": "Unauthorized"}

        response = handler(event, {})
        self.assertDictEqual(response, expected)
