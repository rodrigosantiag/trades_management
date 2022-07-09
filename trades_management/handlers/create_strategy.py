from serpens import api

from entities import User, Strategy
from helpers import authorized
from schemas import StrategySchema


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    body = request.body
    body.update({"user": user})

    try:
        data = StrategySchema.load(body)
    except TypeError as error:
        return 400, {"message": str(error)}

    strategy = Strategy(name=data.name, user=data.user)
    return 201, {"uid": strategy.uid}
