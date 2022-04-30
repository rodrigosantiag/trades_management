from serpens import api

from entities import User, Broker, Account
from helpers import authorized

ALLOWED_QUERY_PARAMS = ["broker_uid", "type_account"]


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    filters = {}
    params = request.query
    broker_uid = params.get("broker_uid")
    type_account = params.get("type_account")
    filters["user"] = user
    result = {"accounts": []}

    if broker_uid:
        filters["broker"] = Broker.get(uid=broker_uid)

    if type_account:
        filters["type_account"] = type_account

    filters = {key: value for key, value in filters.items() if value is not None}
    accounts = Account.select(**filters)[:]

    for account in accounts:
        result["accounts"].append(
            {
                "uid": account.uid,
                "type_account": account.type_account,
                "currency": account.currency,
                "initial_balance": account.initial_balance,
                "current_balance": account.current_balance,
                "broker": {"name": account.broker.name},
            }
        )

    return result
