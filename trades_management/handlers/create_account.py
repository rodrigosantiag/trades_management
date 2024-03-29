from uuid import uuid4

from serpens import api

from entities import User, Broker, Account
from helpers import authorized
from schemas import AccountSchema


@authorized
def handle(request: api.Request):
    payload = request.body
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    broker = Broker.get(uid=payload.get("broker_uid"), user=user)

    if not broker:
        return 400, {"message": "Invalid broker"}

    try:
        data = AccountSchema.load(payload)
    except (KeyError, ValueError, TypeError) as error:
        return 400, {"message": str(error)}

    account = Account(
        uid=uuid4(),
        type_account=data.type_account,
        currency=data.currency,
        initial_balance=data.initial_balance,
        current_balance=data.current_balance,
        broker=broker,
        user=user,
        created_at=data.created_at,
        updated_at=data.updated_at,
    )

    return 201, {"uid": str(account.uid)}
