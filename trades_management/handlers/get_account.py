from serpens import api

from entities import Account, User
from helpers import authorized


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer["user_uuid"]
    account_uuid = request.path.get("uuid")
    user = User.get(uid=user_uuid)
    account = Account.get(uid=account_uuid, user=user)

    if not account:
        return 404, {"error": "Account not found"}

    result = {
        "broker_uuid": str(account.broker.uid),
        "type_account": account.type_account,
        "currency": account.currency,
        "initial_balance": account.initial_balance,
    }

    return result
