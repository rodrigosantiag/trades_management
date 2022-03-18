import json
import unittest
from unittest.mock import patch, MagicMock

from jose import jwt

import helpers
from helpers import get_oauth_token

RESPONSE_DATA = (
    '{"keys": [{"alg": "RS256", "kty": "RSA", "use": "sig", "n": "0wtlJRY9-ru61'
    "LmOgieeI7_rD1oIna9QpBMAOWw8wTuoIhFQFwcIi7MFB7IEfelCPj08vkfLsuFtR8cG07EE4uv"
    "J78bAqRjMsCvprWp4e2p7hqPnWcpRpDEyHjzirEJle1LPpjLLVaSWgkbrVaOD0lkWkP1T1TkrO"
    "set_Obh8BwtO-Ww-UfrEwxTyz1646AGkbT2nL8PX0trXrmira8GnrCkFUgTUS61GoTdb9bCJ19"
    "PLX9Gnxw7J0BtR0GubopXq8KlI0ThVql6ZtVGN2dvmrCPAVAZleM5TVB61m0VSXvGWaF6_GeOh"
    'bFoyWcyUmFvzWhBm8Q38vWgsSI7oHTkEw", "e": "AQAB", "kid": "NEE1QURBOTM4MzI5R'
    'kFDNTYxOTU1MDg2ODgwQ0UzMTk1QjYyRkRFQw", "x5t": "NEE1QURBOTM4MzI5RkFDNTYxOT'
    'U1MDg2ODgwQ0UzMTk1QjYyRkRFQw", "x5c": ["MIIDBzCCAe+gAwIBAgIJNtD9Ozi6j2jJMA'
    "0GCSqGSIb3DQEBCwUAMCExHzAdBgNVBAMTFmRldi04N2V2eDlydS5hdXRoMC5jb20wHhcNMTkw"
    "NjIwMTU0NDU4WhcNMzMwMjI2MTU0NDU4WjAhMR8wHQYDVQQDExZkZXYtODdldng5cnUuYXV0aD"
    "AuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0wtlJRY9+ru61LmOgieeI7/r"
    "D1oIna9QpBMAOWw8wTuoIhFQFwcIi7MFB7IEfelCPj08vkfLsuFtR8cG07EE4uvJ78bAqRjMsC"
    "vprWp4e2p7hqPnWcpRpDEyHjzirEJle1LPpjLLVaSWgkbrVaOD0lkWkP1T1TkrOset/Obh8Bwt"
    "O+Ww+UfrEwxTyz1646AGkbT2nL8PX0trXrmira8GnrCkFUgTUS61GoTdb9bCJ19PLX9Gnxw7J0"
    "BtR0GubopXq8KlI0ThVql6ZtVGN2dvmrCPAVAZleM5TVB61m0VSXvGWaF6/GeOhbFoyWcyUmFv"
    "zWhBm8Q38vWgsSI7oHTkEwIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBQlGX"
    "pmYaXFB7Q3eG69Uhjd4cFp/jAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZIhvcNAQELBQADggEBAIzQ"
    "OF/h4T5WWAdjhcIwdNS7hS2Deq+UxxkRv+uavj6O9mHLuRG1q5onvSFShjECXaYT6OGibn7Ufw"
    "/JSm3+86ZouMYjBEqGh4OvWRkwARy1YTWUVDGpT2HAwtIq3lfYvhe8P4VfZByp1N4lfn6X2NcJ"
    "flG+Q+mfXNmRFyyft3Oq51PCZyyAkU7bTun9FmMOyBtmJvQjZ8RXgBLvu9nUcZB8yTVoeUEg4c"
    "LczQlli/OkiFXhWgrhVr8uF0/9klslMFXtm78iYSgR8/oC+k1pSNd1+ESSt7n6+JiAQ2Co+ZNK"
    'ta7LTDGAjGjNDymyoCrZpeuYQwwnHYEHu/0khjAxhXo="]}]}'
)


class TestHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FRTFRVVJCT1RNNE16ST"
            "VSa0ZETlRZeE9UVTFNRGcyT0Rnd1EwVXpNVGsxUWpZeVJrUkZRdyJ9.eyJpc3MiOiJ"
            "odHRwczovL2Rldi04N2V2eDlydS5hdXRoMC5jb20vIiwic3ViIjoiY"
            "Vc0Q2NhNzl4UmVMV1V6MGFFMkg2a0QwTzNjWEJWdENAY2xpZW50cyIsImF1ZCI6Imh"
            "0dHBzOi8vZXhwZW5zZXMtYXBpIiwiaWF0IjoxNTcyMDA2OTU0LCJleHAiOjE1NzIwM"
            "DY5NjQsImF6cCI6ImFXNENjYTc5eFJlTFdVejBhRTJINmtEME8zY1hCVnRDIiwiZ3R"
            "5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.PUxE7xn52aTCohGiWoSdMBZGiYAHwE5FY"
            "ie0Y1qUT68IHSTXwXVd6hn02HTah6epvHHVKA2FqcFZ4GGv5VTHEvYpeggiiZMgbxF"
            "rmTEY0csL6VNkX1eaJGcuehwQCRBKRLL3zKmA5IKGy5GeUnIbpPHLHDxr-GXvgFzsd"
            "syWlVQvPX2xjeaQ217r2PtxDeqjlf66UYl6oY6AqNS8DH3iryCvIfCcybRZkc_hdy-"
            "6ZMoKT6Piijvk_aXdm7-QQqKJFHLuEqrVSOuBqqiNfVrG27QzAPuPOxvfXTVLXL2je"
            "k5meH6n-VWgrBdoMFH93QEszEDowDAEhQPHVs0xj7SIzA"
        )

    def test_get_oauth_token_none(self):
        authorization_token = None

        with self.assertRaises(Exception) as error:
            get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header is expected")

    def test_get_oauth_token_without_bearer(self):
        authorization_token = "tokentestabcd"

        with self.assertRaises(Exception) as error:
            get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header must start with 'Bearer'")

    def test_get_oauth_token__without_token(self):
        authorization_token = "Bearer "

        with self.assertRaises(Exception) as error:
            get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Token not found")

    def test_get_oauth_token_invalid_format(self):
        authorization_token = "Bearer testtokenabcd invalid"

        with self.assertRaises(Exception) as error:
            get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header must be Bearer token")

    def test_get_oauth_token_succeed(self):
        authorization_token = "Bearer testtokenabcd"

        result = get_oauth_token(authorization_token)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "testtokenabcd")

    @patch("helpers.jwt.decode")
    @patch("helpers.urlopen")
    def test_authorized_token_expired(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = jwt.ExpiredSignatureError("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        @helpers.authorized
        def handler(request):
            return json.dumps({"error": f"Token {request.headers.get('Authorization')} expired"})

        with self.assertRaises(Exception) as error:
            handler(event, None)
            self.assertEqual(str(error), "token is expired")

    @patch("helpers.jwt.decode")
    @patch("helpers.urlopen")
    def test_authorized_claims_error(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = jwt.JWTClaimsError("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        @helpers.authorized
        def handler(request):
            return ""

        with self.assertRaises(Exception) as error:
            handler(event, None)
            self.assertEqual(str(error), "please check the audience and issuer")

    @patch("helpers.jwt.decode")
    @patch("helpers.urlopen")
    def test_authorized_invalid_header(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = Exception("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        @helpers.authorized
        def handler(request):
            return ""

        with self.assertRaises(Exception) as error:
            handler(event, None)
            self.assertEqual(str(error), "Unable to parse authentication Token")

    @patch("helpers.jwt.get_unverified_header", lambda x: {"kid": "1234"})
    @patch("helpers.jwt.decode", lambda x, y, algorithms, audience, issuer: {})
    @patch("helpers.urlopen")
    def test_authorized_unable_find_token(self, m_urlopen):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        @helpers.authorized
        def handler(request):
            return ""

        with self.assertRaises(Exception) as error:
            handler(event, None)
            self.assertEqual(str(error), "Unable to find appropriate key")

    @patch("helpers.jwt.decode", lambda x, y, algorithms, audience, issuer: {})
    @patch("helpers.urlopen")
    def test_authorized_succeed(self, m_urlopen):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA

        event = {"headers": {"Authorization": f"Bearer {self.token}"}}
        expected = {
            "headers": {"Access-Control-Allow-Origin": "*"},
            "statusCode": 200,
            "body": json.dumps({"token": f"Bearer {self.token}"}),
        }

        @helpers.authorized
        def handler(request):
            return json.dumps({"token": request.headers.get("Authorization")})

        response = handler(event, None)

        self.assertDictEqual(response, expected)
