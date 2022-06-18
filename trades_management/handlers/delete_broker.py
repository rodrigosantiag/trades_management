from serpens import api

from entities import Broker, User
from helpers import authorized


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    broker_uuid = request.path.get("uuid")

    if not broker_uuid:
        return 400, {"error": "Invalid broker"}

    user = User.get(uid=user_uuid)

    try:
        broker = Broker.get(uid=broker_uuid, user=user)
    except ValueError:
        broker = None

    if not broker:
        return 400, {"error": "Invalid broker"}

    broker.delete()

    return 204, None
