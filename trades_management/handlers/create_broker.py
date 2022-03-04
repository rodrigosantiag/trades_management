from uuid import uuid4

from pony.orm import db_session
from serpens import api

from entities import Broker
from schemas import BrokerSchema


@api.handler
@db_session
def handle(request: api.Request):
    try:
        data = BrokerSchema.load(request.body)
    except (TypeError, ValueError) as error:
        return 400, {"error": f"{error}"}

    broker = Broker(uid=uuid4(), name=data.name, user=data.user_id)

    return 201, {"uid": str(broker.uid)}
