from pony.orm import db_session
from serpens import api

from entities import Broker


@api.handler
@db_session
def handle(request: api.Request):
    user_id = request.query.get("user_id")

    if not user_id:
        return 400, {"error": "Missing user ID"}

    user_brokers = Broker.select(user=user_id)[:]
    brokers = []

    for broker in user_brokers:
        item = {"uid": broker.uid, "name": broker.name, "accounts": []}
        accounts = list(broker.accounts)

        for account in accounts:
            item["accounts"].append(
                {
                    "uid": account.uid,
                    "type_account": account.type_account,
                    "currency": account.currency,
                    "initial_balance": account.initial_balance,
                    "current_balance": account.current_balance,
                }
            )

        brokers.append(item)

    return {"brokers": brokers}
