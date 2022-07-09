from datetime import datetime

from serpens import api

from entities import Broker, User
from helpers import authorized
from schemas import BrokerSchema


@authorized
def handle(request: api.Request):
    payload = request.body
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    broker_uuid = request.path.get("uuid")

    try:
        broker = Broker.get(uid=broker_uuid, user=user)
    except (ValueError, KeyError, IndexError):
        broker = None

    if not broker:
        return 404, {"message": "Broker not found"}

    try:
        data = BrokerSchema.load(payload)
    except (TypeError, ValueError) as error:
        return 400, {"message": f"{error}"}

    broker.name = data.name
    broker.updated_at = datetime.utcnow()

    return 204, None
