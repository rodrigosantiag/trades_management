from serpens import api

from entities import Broker, User
from helpers import authorized


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    broker_uuid = request.path.get("uuid")

    if not broker_uuid:
        return 404, {"error": "Broker not found"}

    user = User.get(uid=user_uuid)

    try:
        broker = Broker.get(uid=broker_uuid, user=user)
    except ValueError:
        return 404, {"error": "Broker not found"}

    if not broker:
        return 404, {"error": "Broker not found"}

    broker.delete()

    return 204, None
