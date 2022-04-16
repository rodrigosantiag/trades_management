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
        return 404, {"error": "Broker not found"}

    try:
        data = BrokerSchema.load(payload)
    except (TypeError, ValueError) as error:
        return 400, {"error": f"{error}"}

    broker.name = data.name
    updated_broker = broker.to_dict(only=["uid", "name"])
    updated_broker["accounts"] = []
    broker_accounts = list(broker.accounts)

    if broker_accounts:
        for account in broker_accounts:
            updated_broker["accounts"].append(
                account.to_dict(
                    only=["uid", "type_account", "currency", "initial_balance", "current_balance"]
                )
            )

    return 200, updated_broker
