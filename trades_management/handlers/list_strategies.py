from entities import User, Strategy
from helpers import authorized
from serpens import api


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    user_strategies = []

    strategies = Strategy.select(user=user)[:]

    for strategy in strategies:
        user_strategies.append(
            {
                "uid": strategy.uid,
                "name": strategy.name,
            }
        )

    return {"strategies": user_strategies}
