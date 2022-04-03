from uuid import uuid4

from serpens import api

from entities import Broker, User
from helpers import authorized
from schemas import BrokerSchema


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)

    try:
        data = BrokerSchema.load(request.body)
    except (TypeError, ValueError) as error:
        return 400, {"error": f"{error}"}

    broker = Broker(uid=uuid4(), name=data.name, user=user)

    return 201, {"uid": str(broker.uid)}
