import unittest
from unittest.mock import patch, MagicMock

from jose import jwt

from handlers import authorize

RESPONSE_DATA = (
    '{"keys": [{"alg": "RS256", "kty": "RSA", "use": "sig", "n": "v1iVDT-fjHxSUsx-7uLkLmy4HbpVwtt3_'
    "PTlvSweVzgFiUgIRRC_MAfvfM3-tepefOOmSc7Akm4DZTQjEr8rURMhLB2Nro_ynSMaJe_hcF-dulEcMHUKWZnObPkDK6o"
    "11yTiYhh1bq7BH8s_mRmgKKEumxZHR4zGnVKpQWdgleomlClRlAWBrcshDL1l_tAWl9gRf_m5z3TE5_Gebnx_YT0ptXVi1"
    "gB3acTxcNdsRHQYoaDhFhG7bAKHMdelMFZzK8a4hgcCACYXOpl_7TZPCQYhTUc4ToVVcsVE2dyxsRvJY7k4khPhpSO5fFy"
    '2WYR-E9z4ZsLUDs_Wxb_6OjZ-JQ", "e": "AQAB", "kid": "pQrtUF-LUK3Zzh-JhjCRI", "x5t": "ZLwJketm1Lc'
    'Nyj1y88jx5qJxyMM", "x5c": ["MIIDDTCCAfWgAwIBAgIJb7f//QPd9wgWMA0GCSqGSIb3DQEBCwUAMCQxIjAgBgNVBA'
    "MTGWRldi1vY3B2aGl4by51cy5hdXRoMC5jb20wHhcNMjIwMzAyMTMzNDE5WhcNMzUxMTA5MTMzNDE5WjAkMSIwIAYDVQQD"
    "ExlkZXYtb2NwdmhpeG8udXMuYXV0aDAuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv1iVDT+fjHxSUs"
    "x+7uLkLmy4HbpVwtt3/PTlvSweVzgFiUgIRRC/MAfvfM3+tepefOOmSc7Akm4DZTQjEr8rURMhLB2Nro/ynSMaJe/hcF+d"
    "ulEcMHUKWZnObPkDK6o11yTiYhh1bq7BH8s/mRmgKKEumxZHR4zGnVKpQWdgleomlClRlAWBrcshDL1l/tAWl9gRf/m5z3"
    "TE5/Gebnx/YT0ptXVi1gB3acTxcNdsRHQYoaDhFhG7bAKHMdelMFZzK8a4hgcCACYXOpl/7TZPCQYhTUc4ToVVcsVE2dyx"
    "sRvJY7k4khPhpSO5fFy2WYR+E9z4ZsLUDs/Wxb/6OjZ+JQIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBB"
    "QkebB0DuquSt6t0zvs2qZRCqmzeTAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZIhvcNAQELBQADggEBAFy3bHZkYcuIw+YGebPr"
    "J1jGkYpU3s/d1qtLC2fNPzFh+JQshHs9q2Yr/MD+qHXI05ICr4zSb0hK3E/KrAXfeJypyS3rXpAqHIlVTShFsggvkp7WWE"
    "PWVE2d7CensvbjK4xQxr+KZ6EQLmoZmEyPrgeDkwVmu8lxZxYz8dpGrKwJHLz4klTswErokBrtReZ9j/JFhXY4KMDxrg/Z"
    "NAAkJSE1nZqJkJfsuLHpWp2EtACYUnh+6qCvxL07JQ7aHxI3Hyim2lBzPfdhk/JhzHOK9nwUkD0atQStsLk28YQOiMfR3q"
    'W9qSFnABGthLmgkcBRrI1wMTcDqOEiDkF9i8qonYE="]}, {"alg": "RS256", "kty": "RSA", "use": "sig", "n'
    '": "6cqHTpdWd1OwUm7XVvoJ9ElHnMge24ACk-lJgNDizzWOVuySKB9Fa0lsqPnNly9UM_YWgz1zBm9Kw2sgKkti3d1IwQ'
    "mEhGLCW5bcRzNnlVM4SeGlfzGrGmBcImbI4IIz2Yrk4n7VcKHrA7UC_CWIlHR3-bxKzPMuwhY0Fweod2u3RSi2rha02gQf"
    "7VzlRm2JSoznx-GCWyzn8Kyk0xL5bi1ZZeUXO0zRGsgu5l1lhFvFqLg7a-rCaKNShTlxsi0sL-PUumxMIDqP2wb4Na2Pjh"
    'lt9rPcMrC_4RLRTkqoUUF4NN0KZF3tjZfgvyfmAtVPLUG_pugoXC1FiJjDCGmmAw", "e": "AQAB", "kid": "J8Bbus'
    'y3cl7Yrz19lyAD-", "x5t": "0FR_Hi3SyVFeKZHTTW090owCqC0", "x5c": ["MIIDDTCCAfWgAwIBAgIJFRdmE2hle'
    "DZ4MA0GCSqGSIb3DQEBCwUAMCQxIjAgBgNVBAMTGWRldi1vY3B2aGl4by51cy5hdXRoMC5jb20wHhcNMjIwMzAyMTMzNDE"
    "5WhcNMzUxMTA5MTMzNDE5WjAkMSIwIAYDVQQDExlkZXYtb2NwdmhpeG8udXMuYXV0aDAuY29tMIIBIjANBgkqhkiG9w0BA"
    "QEFAAOCAQ8AMIIBCgKCAQEA6cqHTpdWd1OwUm7XVvoJ9ElHnMge24ACk+lJgNDizzWOVuySKB9Fa0lsqPnNly9UM/YWgz1"
    "zBm9Kw2sgKkti3d1IwQmEhGLCW5bcRzNnlVM4SeGlfzGrGmBcImbI4IIz2Yrk4n7VcKHrA7UC/CWIlHR3+bxKzPMuwhY0F"
    "weod2u3RSi2rha02gQf7VzlRm2JSoznx+GCWyzn8Kyk0xL5bi1ZZeUXO0zRGsgu5l1lhFvFqLg7a+rCaKNShTlxsi0sL+P"
    "UumxMIDqP2wb4Na2Pjhlt9rPcMrC/4RLRTkqoUUF4NN0KZF3tjZfgvyfmAtVPLUG/pugoXC1FiJjDCGmmAwIDAQABo0IwQ"
    "DAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTjNGkc1HZUpYQGKxJ3wh2bJnclKjAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZ"
    "IhvcNAQELBQADggEBAEaAY17eVO6HyOmTHxx5B3C4ENovS6En2hk9dqhVe3Uwo3+inTYn2a/pTyhdXduRwKzEWXJZAEzuR"
    "ZjhrN67WTl8xM2l8RJpdz0zG1I/n01lBxcY24ZmCDgYPpz+7A2RWeDJVzNrCf7tC7Dn72yZFhV/JxgiENhSy9FT3zJ9UXs"
    "XexsZOFUxRab0nwAIgAp9bxsoEI1T0RIcG0nQ6TKf2EDOJJtVjpsQU2RAI11n0chQeTxSAxCuLysdbs1UjFlsTRHk4dj0u"
    'vpBxnt1Gt0fX695yRx/pHUJkAxmNZCQXXvKGUQ2q8j/GudTdiTKUVrz9H4tNJyfPksI+CP/SOw4NbU="]}]}'
)


class TestAuthorize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBRcnRVRi1MVUszWnpoLUpoakNSSSJ9.eyJpc3MiO"
            "iJodHRwczovL2Rldi1vY3B2aGl4by51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8N2NjNzM1OWEtZTU4NS0"
            "0YzNiLWI1NjctNjdmMzJiZTA2NTE0IiwiYXVkIjoiaHR0cHM6Ly9hNnJ5MnVqMzk2LmV4ZWN1dGUtYXBpLnVzL"
            "WVhc3QtMS5hbWF6b25hd3MuY29tL3YxIiwiaWF0IjoxNjQ4OTE0ODYwLCJleHAiOjE2NDkwMDEyNjAsImF6cCI"
            "6IlJJYTB0MDE1ekd3TXRUWTE4Rm9jZnNscm9Fa2xKRXpzIiwiZ3R5IjoicGFzc3dvcmQifQ.lxrYjcFwG2zWP4"
            "8sJ51GLYrUgnWh-0bO0vDCZCFr4snCRuZBsPvY6MV9SGsr6qEUWf-I20fj6vxOI6XXTVTrZ6dW41-lyJo42IkC"
            "uDzKawPSKm9kPlzHW-2yDEtDuRIFOxBFj3k_dKlXVUrPZIz5rLW4zbZZLhHSZ5cpxIP6BVK3fnTb26qdQAV5LB"
            "sHcEH17YBNwJOwQeNwyKQBTc_gsDkfBtAddFNXuswwkNSyjhvL5K8hy29uurYcsstS8sZUyNRiH1QMLet3uoaT"
            "xni3pWLljp95rSnz5MuFSToLhvJffq3-Kp22b66ty2mGrSXQ-hP20Bjrw5nhZe6fQ0zJzg"
        )

    def test_get_oauth_token_none(self):
        authorization_token = None

        with self.assertRaises(Exception) as error:
            authorize.get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header is expected")

    def test_get_oauth_token_without_bearer(self):
        authorization_token = "tokentestabcd"

        with self.assertRaises(Exception) as error:
            authorize.get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header must start with 'Bearer'")

    def test_get_oauth_token__without_token(self):
        authorization_token = "Bearer "

        with self.assertRaises(Exception) as error:
            authorize.get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Token not found")

    def test_get_oauth_token_invalid_format(self):
        authorization_token = "Bearer testtokenabcd invalid"

        with self.assertRaises(Exception) as error:
            authorize.get_oauth_token(authorization_token)
            self.assertEqual(str(error), "Authorization header must be Bearer token")

    def test_get_oauth_token_succeed(self):
        authorization_token = "Bearer testtokenabcd"

        result = authorize.get_oauth_token(authorization_token)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "testtokenabcd")

    @patch("handlers.authorize.jwt.decode")
    @patch("handlers.authorize.urlopen")
    def test_authorized_token_expired(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = jwt.ExpiredSignatureError("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        with self.assertRaises(Exception) as error:
            authorize.handle(event, {})
            self.assertEqual(str(error), "token is expired")

    @patch("handlers.authorize.jwt.decode")
    @patch("handlers.authorize.urlopen")
    def test_authorized_claims_error(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = jwt.JWTClaimsError("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        with self.assertRaises(Exception) as error:
            authorize.handle(event, {})
            self.assertEqual(str(error), "please check the audience and issuer")

    @patch("handlers.authorize.jwt.decode")
    @patch("handlers.authorize.urlopen")
    def test_authorized_invalid_header(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        m_jwt.side_effect = Exception("Exception test")
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        with self.assertRaises(Exception) as error:
            authorize.handle(event, {})
            self.assertEqual(str(error), "Unable to parse authentication Token")

    @patch("handlers.authorize.jwt.get_unverified_header", lambda x: {"kid": "1234"})
    @patch("handlers.authorize.jwt.decode", lambda x, y, algorithms, audience, issuer: {})
    @patch("handlers.authorize.urlopen")
    def test_authorized_unable_find_token(self, m_urlopen):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA
        event = {"headers": {"Authorization": f"Bearer {self.token}"}}

        with self.assertRaises(Exception) as error:
            authorize.handle(event, {})
            self.assertEqual(str(error), "Unable to find appropriate key")

    @patch("handlers.authorize.jwt.decode")
    @patch("handlers.authorize.urlopen")
    def test_authorized_invalid_jwt_decoded(self, m_urlopen, m_jwt):
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA

        m_jwt.return_value = {
            "iss": "https://test.com/",
            "sub": "abcde",
            "aud": "https://test.com/v1",
            "iat": 1648914860,
            "exp": 1649001260,
            "azp": "RIa0t015zGwMtTY18FocfslroEklJEzs",
            "gty": "password",
        }

        event = {
            "headers": {"Authorization": f"Bearer {self.token}"},
            "methodArn": "arn:aws:execute-api:us-east-1:4343248168333:siu8zlsx0h/v1/GET/",
        }

        with self.assertRaises(Exception) as error:
            authorize.handle(event, {})
            self.assertEqual(str(error), "Unauthorized")

    @patch("handlers.authorize.settings")
    @patch("handlers.authorize.jwt.timegm")
    @patch("handlers.authorize.urlopen")
    def test_authorized_succeed(self, m_urlopen, m_datetime, m_settings):
        m_settings.return_value = MagicMock()
        m_settings.JWKS_DOMAIN = "dev-ocpvhixo.us.auth0.com"
        m_settings.API_AUDIENCE = "https://a6ry2uj396.execute-api.us-east-1.amazonaws.com/v1"
        m_datetime.return_value = 1648919772
        m_urlopen.return_value = MagicMock()
        m_urlopen.return_value.read.return_value = RESPONSE_DATA

        event = {
            "headers": {"Authorization": f"Bearer {self.token}"},
            "methodArn": "arn:aws:execute-api:us-east-1:4343248168333:siu8zlsx0h/v1/GET/",
        }

        expected = {
            "principalId": "auth0|7cc7359a-e585-4c3b-b567-67f32be06514",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": [
                            "arn:aws:execute-api:us-east-1:4343248168333:siu8zlsx0h/v1/*/*"
                        ],
                    }
                ],
            },
            "context": {"sub": "auth0", "user_uuid": "7cc7359a-e585-4c3b-b567-67f32be06514"},
        }

        response = authorize.handle(event, {})

        self.assertDictEqual(response, expected)
