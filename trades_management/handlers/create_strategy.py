from uuid import uuid4

from serpens import api

from entities import User, Strategy
from helpers import authorized
from schemas import StrategySchema


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    payload = request.body
    payload.update({"user_id": user.id})

    try:
        data = StrategySchema.load(payload)
    except (ValueError, TypeError) as error:
        return 400, {"message": f"{error}"}

    strategy = Strategy(uid=uuid4(), name=data.name, user=user)

    return 201, {"uid": strategy.uid}
