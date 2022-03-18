from serpens import envvars

APPNAME = "trades-management"
VERSION = "0.1.0"

DATABASE_URL = envvars.get("DATABASE_URL")

# Authorizer
JWKS_URL = envvars.get("JWKS_URL", "http://foo.com")
API_AUDIENCE = envvars.get("API_AUDIENCE", "http://foo.com")
