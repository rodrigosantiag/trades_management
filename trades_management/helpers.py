import logging
from functools import wraps
from typing import Union, Tuple, Any

from pony.orm import db_session
from serpens import api

from entities import User

logger = logging.getLogger(__name__)


def authorized(func):
    @wraps(func)
    @api.handler
    @db_session
    def wrapper(request: api.Request) -> Union[Tuple[int, Any], str]:
        user_uuid = request.authorizer.get("user_uuid")
        user = User.get(uid=user_uuid)

        if not user:
            return 401, {"message": "Unauthorized"}

        logger.debug(f"Injected authorization: {request.authorizer}")

        response = func(request)
        return response

    return wrapper
