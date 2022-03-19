import json
from typing import Optional
from urllib.request import urlopen

from jose import jwt

import authpolicy
import settings


def get_oauth_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        raise Exception("Authorization header is expected")

    authorization_parts = authorization.split()

    if authorization_parts[0].lower() != "bearer":
        raise Exception("Authorization header must start with 'Bearer'")
    elif len(authorization_parts) == 1:
        raise Exception("Token not found")
    elif len(authorization_parts) > 2:
        raise Exception("Authorization header must be Bearer token")

    return authorization_parts[1]


def handle(event, context):
    authorization = event.get("headers", {}).get("Authorization")
    token = get_oauth_token(authorization)
    method_arn = event.get("methodArn")
    jsonurl = urlopen(f"https://{settings.JWKS_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.API_AUDIENCE,
                issuer=f"https://{settings.JWKS_DOMAIN}/",
            )
        except jwt.ExpiredSignatureError:
            raise Exception("token is expired")
        except jwt.JWTClaimsError:
            raise Exception("please check the audience and issuer")
        except Exception:
            raise Exception("Unable to parse authentication token")

        policy = authpolicy.AuthPolicy(payload["sub"], method_arn)
        policy.allowAllMethods()
        return policy.build()

    raise Exception("Unable to find appropriate key")
