from datetime import datetime

from serpens import api

from entities import User, Account, Broker
from helpers import authorized
from schemas import AccountSchema


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    account_uuid = request.path.get("uuid")
    body = request.body
    broker = None
    account = None

    try:
        broker = Broker.get(uid=body.get("broker_id"), user=user)
        account = Account.get(user=user, uid=account_uuid)
    except (KeyError, ValueError, IndexError):
        account = None

    if not account or not broker:
        return 400, {"message": "Invalid broker or account"}

    payload = {
        "type_account": body.get("type_account"),
        "broker_id": broker.id,
        "currency": body.get("currency"),
        "user_id": user.id,
        "initial_balance": body.get("initial_balance"),
    }

    try:
        data = AccountSchema.load(payload)
    except (TypeError, ValueError) as error:
        return 400, {"message": f"{error}"}

    account.type_account = data.type_account
    account.broker = broker
    account.currency = data.currency
    account.initial_balance = data.initial_balance
    account.updated_at = datetime.utcnow()

    return 204, None
