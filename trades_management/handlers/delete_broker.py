from pony.orm import db_session
from serpens import api

from entities import Broker


@api.handler
@db_session
def handle(request: api.Request):
    payload = request.body

    try:
        broker = Broker.get(uid=payload["uid"], user=payload["user_id"])
    except (ValueError, KeyError, IndexError):
        broker = None

    if not broker:
        return 404, {"error": "Broker not found"}

    broker.delete()

    return 204, None
