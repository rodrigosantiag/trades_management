from serpens import api

from entities import Broker, User
from helpers import authorized


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)

    user_brokers = Broker.select(user=user)[:]
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
