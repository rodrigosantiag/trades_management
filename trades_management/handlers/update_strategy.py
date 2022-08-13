from serpens import api

from entities import User, Strategy
from helpers import authorized
from schemas import StrategySchema


@authorized
def handle(request: api.Request):
    user_uuid = request.authorizer.get("user_uuid")
    user = User.get(uid=user_uuid)
    strategy_uuid = request.path.get("uuid")
    payload = request.body

    try:
        strategy = Strategy.get(user=user, uid=strategy_uuid)
    except (KeyError, IndexError, ValueError):
        strategy = None

    if not strategy:
        return 404, {"message": "Strategy not found"}

    try:
        data = StrategySchema.load(payload)
    except (TypeError, ValueError) as error:
        return 400, {"message": f"{error}"}

    strategy.name = data.name

    return 204, None
