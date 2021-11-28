from serpens import envvars

APPNAME = "trades_management"
VERSION = "0.1.0"

DATABASE_URL = envvars.get("DATABASE_URL", "sqlite://:memory:")
