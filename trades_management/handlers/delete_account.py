from serpens import api

from entities import User, Account
from helpers import authorized


@authorized
def handle(request: api.Request):
    account_uuid = request.path.get("uuid")
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)

    try:
        account = Account.get(user=user, uid=account_uuid)
    except ValueError:
        account = None

    if account is None:
        return 400, {"error": "Invalid account"}

    account.delete()

    return 204, None
