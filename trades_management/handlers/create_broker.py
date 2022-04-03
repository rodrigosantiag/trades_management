from uuid import uuid4

from pony.orm import db_session
from serpens import api

from entities import Broker, User
from schemas import BrokerSchema


@api.handler
@db_session
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)

    if not user:
        return 401, {"error": "Unauthorized"}

    try:
        data = BrokerSchema.load(request.body)
    except (TypeError, ValueError) as error:
        return 400, {"error": f"{error}"}

    broker = Broker(uid=uuid4(), name=data.name, user=user)

    return 201, {"uid": str(broker.uid)}
