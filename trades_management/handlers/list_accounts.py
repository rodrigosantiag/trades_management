from serpens import api

from helpers import authorized

ALLOWED_QUERY_PARAMS = ["broker_uid", "type_account"]


@authorized
def handle(request: api.Request):
    pass
