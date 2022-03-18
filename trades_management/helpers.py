import json
from functools import wraps
from typing import Tuple, Union, Optional, Dict
from urllib.request import urlopen

from jose import jwt
from serpens import api

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


def authorized(func):
    @wraps(func)
    @api.handler
    def wrapper(request: api.Request) -> Union[Tuple[int, Dict[str, str]], str]:
        authorization = request.headers.get("Authorization")
        token = get_oauth_token(authorization)
        jsonurl = urlopen(f"{settings.JWKS_URL}/.well-known/jwks.json")
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
                jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=settings.API_AUDIENCE,
                    issuer=settings.JWKS_URL,
                )
            except jwt.ExpiredSignatureError:
                return 401, {"error": "token is expired"}
            except jwt.JWTClaimsError:
                return 401, {"error": "please check the audience and issuer"}
            except Exception:
                return 401, {"error": "Unable to parse authentication token"}

            response = func(request)
            return response

        return 401, {"error": "Unable to find appropriate key"}

    return wrapper
