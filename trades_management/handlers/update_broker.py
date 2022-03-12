from pony.orm import db_session
from serpens import api

from entities import Broker
from schemas import BrokerSchema


@api.handler
@db_session
def handle(request: api.Request):
    payload = request.body

    try:
        broker = Broker.get(uid=payload["uid"], user=payload["user_id"])
    except (ValueError, KeyError, IndexError):
        broker = None

    if not broker:
        return 404, {"message": "Broker not found"}

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
